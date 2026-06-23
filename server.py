"""
server.py — Family Office Platform · Web Server
════════════════════════════════════════════════
Serves the dashboard AND handles PDF upload/import/routing.

Replaces: python -m http.server 8765 (static-only)
Adds:
  POST /route   → runs route_document.py  → returns {domain, reason, …}
  POST /upload  → runs import_statement.py → returns full import result
  POST /save    → stores file to uploads/, no classification
  POST /chat    → calls Claude API with archive context → returns {reply}

Usage:  python server.py
"""
import http.server, socketserver, json, os, sys, re, subprocess, tempfile, urllib.request, urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, timezone

PROJECT_DIR  = Path(__file__).resolve().parent
DIST_DIR     = PROJECT_DIR / "dashboard-dist"
SCRIPTS_DIR  = PROJECT_DIR / "scripts"
UPLOADS_DIR  = PROJECT_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)
PORT         = 8765


class FamilyOfficeHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST_DIR), **kwargs)

    # ── CORS pre-flight ──────────────────────────────────────────────────────
    def do_OPTIONS(self):
        self.send_response(204)
        self._cors_headers()
        self.end_headers()

    # ── GET /news & /statements ───────────────────────────────────────────────
    def do_GET(self):
        if self.path.startswith("/statements/"):
            self._serve_statement()
        elif self.path.startswith("/uploads/"):
            self._serve_file(UPLOADS_DIR, "/uploads/")
        elif self.path == "/api/imports":
            self._handle_imports()
        elif self.path == "/api/deals":
            self._handle_deals()
        elif self.path == "/api/deal-updates":
            self._handle_deal_updates()
        elif self.path == "/api/cashflow":
            self._handle_cashflow()
        elif self.path == "/api/pipeline":
            self._handle_pipeline()
        elif self.path.startswith("/news"):
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            sources = params.get("sources", ["reuters,cnbc,ft,economist,federalreserve"])[0].split(",")
            self._handle_news(sources)
        else:
            super().do_GET()

    def _handle_imports(self):
        """Return the imports-registry.json as JSON."""
        registry = PROJECT_DIR / "ops-dashboard-demo" / "src" / "data" / "imports-registry.json"
        if registry.exists():
            data = json.loads(registry.read_text(encoding="utf-8"))
        else:
            data = []
        self._json(data)

    def _handle_deals(self):
        """Return all deal JSON files from deals/ directory."""
        deals_dir = PROJECT_DIR / "deals"
        deals = []
        if deals_dir.exists():
            for f in sorted(deals_dir.glob("**/*.json")):
                try:
                    deals.append(json.loads(f.read_text(encoding="utf-8")))
                except Exception:
                    pass
        self._json({"deals": deals, "count": len(deals)})

    def _handle_deal_updates(self):
        """Return recent deal updates from deal-updates/ directory."""
        updates_dir = PROJECT_DIR / "deal-updates"
        updates = []
        if updates_dir.exists():
            for f in sorted(updates_dir.rglob("*.json"), reverse=True)[:100]:
                try:
                    obj = json.loads(f.read_text(encoding="utf-8"))
                    # Add the relative path for reference
                    obj["_file"] = str(f.relative_to(PROJECT_DIR))
                    updates.append(obj)
                except Exception:
                    pass
        self._json({"updates": updates, "count": len(updates)})

    def _handle_cashflow(self):
        """Return cashflow data shaped for the dashboard: {snapshot, sources}."""
        cf_file = PROJECT_DIR / "cashflow" / "cashflow.json"
        for path in [cf_file, PROJECT_DIR / "cashflow.json"]:
            if path.exists():
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                    # Extract latest runway snapshot as `snapshot`
                    snaps = data.get("runway_snapshots", [])
                    snapshot = snaps[-1] if snaps else data.get("snapshot")
                    # Build sources list from items joined with source names
                    source_map = {s["id"]: s["name"] for s in data.get("sources", [])}
                    sources = []
                    for item in data.get("items", []):
                        sources.append({
                            "name":       source_map.get(item.get("source_id"), "—"),
                            "type":       item.get("category", "—"),
                            "period":     item.get("period", "—"),
                            "amount_usd": item.get("amount_usd"),
                        })
                    self._json({"snapshot": snapshot, "sources": sources})
                    return
                except Exception:
                    pass
        self._json({"snapshot": None, "sources": []})

    def _handle_pipeline(self):
        """Return pipeline stage counts across all deal-updates/ JSON files.
        Follows the INGEST → PROCESS → UPDATE → STORE model."""
        updates_dir = PROJECT_DIR / "deal-updates"
        review_dir  = updates_dir / "_needs-review"
        stages = {"ingest": 0, "process": 0, "update": 0, "store": 0, "needs_review": 0}
        recent = []
        for f in sorted(updates_dir.rglob("*.json"), reverse=True):
            if "_raw" in f.parts:
                continue
            try:
                obj = json.loads(f.read_text(encoding="utf-8"))
                if obj.get("needs_review") or str(f).startswith(str(review_dir)):
                    stages["needs_review"] += 1
                else:
                    stage = obj.get("pipeline_stage", "store")
                    stages[stage] = stages.get(stage, 0) + 1
                if len(recent) < 10:
                    recent.append({
                        "id":             obj.get("id"),
                        "deal_name":      obj.get("deal_name"),
                        "update_type":    obj.get("update_type"),
                        "pipeline_stage": obj.get("pipeline_stage", "store"),
                        "needs_review":   obj.get("needs_review", False),
                        "stored_at":      (obj.get("pipeline_timestamps") or {}).get("stored_at"),
                        "confidence_score": obj.get("confidence_score"),
                    })
            except Exception:
                pass
        total = sum(stages.values())
        self._json({
            "stages":         stages,
            "total":          total,
            "recent":         recent,
            "pipeline_order": ["ingest", "process", "update", "store"],
        })

    def _serve_file(self, root_dir, path_prefix):
        filename = self.path[len(path_prefix):].split("?")[0]
        if ".." in filename or "/" in filename:
            self.send_error(400, "Bad path")
            return
        filepath = root_dir / filename
        if not filepath.exists():
            self.send_error(404, f"File not found: {filename}")
            return
        ext = filepath.suffix.lower()
        mime = {
            ".pdf":  "application/pdf",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".xls":  "application/vnd.ms-excel",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".doc":  "application/msword",
            ".csv":  "text/csv",
            ".png":  "image/png",
            ".jpg":  "image/jpeg",
            ".jpeg": "image/jpeg",
        }.get(ext, "application/octet-stream")
        file_size = filepath.stat().st_size

        # ── Byte-range support (required for browser PDF viewers) ──────────
        range_header = self.headers.get("Range", "")
        if range_header and range_header.startswith("bytes="):
            try:
                rng    = range_header[6:].split("-")
                start  = int(rng[0]) if rng[0] else 0
                end    = int(rng[1]) if len(rng) > 1 and rng[1] else file_size - 1
                end    = min(end, file_size - 1)
                length = end - start + 1
                with open(filepath, "rb") as f:
                    f.seek(start)
                    data = f.read(length)
                self.send_response(206)  # Partial Content
                self.send_header("Content-Type", mime)
                self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
                self.send_header("Content-Length", str(length))
                self.send_header("Accept-Ranges", "bytes")
                self.send_header("Content-Disposition", f'inline; filename="{filename}"')
                self._cors_headers()
                self.end_headers()
                self.wfile.write(data)
                return
            except Exception:
                pass  # Fall through to full-file response

        with open(filepath, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(file_size))
        self.send_header("Accept-Ranges", "bytes")      # ← tells browser range requests are OK
        self.send_header("Content-Disposition", f'inline; filename="{filename}"')
        self._cors_headers()
        self.end_headers()
        self.wfile.write(data)

    def _serve_statement(self):
        self._serve_file(PROJECT_DIR / "demo-statements", "/statements/")

    def _handle_news(self, sources):
        RSS_FEEDS = {
            "reuters":       ("Reuters",         "https://feeds.reuters.com/reuters/businessNews"),
            "cnbc":          ("CNBC",             "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114"),
            "wsj":           ("Wall Street Journal", "https://feeds.a.wsj.com/rss/RSSMarketsMain.xml"),
            "ft":            ("Financial Times",  "https://www.ft.com/rss/home/us"),
            "economist":     ("The Economist",    "https://www.economist.com/finance-and-economics/rss.xml"),
            "barrons":       ("Barron's",         "https://www.barrons.com/xml/rss/3_7551.xml"),
            "federalreserve":("Federal Reserve",  "https://www.federalreserve.gov/feeds/press_all.xml"),
            "morningstar":   ("Morningstar",      "https://www.morningstar.com/rss/articles"),
            "bloomberg":     ("Bloomberg",        None),   # no public RSS
        }
        articles = []
        for src in sources:
            src = src.strip()
            entry = RSS_FEEDS.get(src)
            if not entry or not entry[1]:
                continue
            label, url = entry
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; FamilyOfficePlatform/1.0)"})
                with urllib.request.urlopen(req, timeout=8) as resp:
                    raw = resp.read()
                root = ET.fromstring(raw)
                ns = {"atom": "http://www.w3.org/2005/Atom"}
                # Handle both RSS 2.0 and Atom
                items = root.findall(".//item") or root.findall(".//atom:entry", ns)
                for item in items[:8]:
                    def _txt(tag, alt=""):
                        el = item.find(tag) or item.find("atom:" + tag, ns)
                        return (el.text or "").strip() if el is not None else alt
                    title = _txt("title")
                    link  = _txt("link") or _txt("guid")
                    # Atom link is an attribute
                    link_el = item.find("atom:link", ns)
                    if link_el is not None and not link:
                        link = link_el.get("href", "")
                    pub   = _txt("pubDate") or _txt("updated") or _txt("published")
                    desc  = re.sub(r"<[^>]+>", "", _txt("description") or _txt("summary"))[:200]
                    if title and link:
                        articles.append({"source": label, "source_key": src, "title": title, "link": link, "pub": pub, "desc": desc.strip()})
            except Exception as exc:
                articles.append({"source": label, "source_key": src, "title": f"[Could not load {label}]", "link": "", "pub": "", "desc": str(exc)[:120], "error": True})
        # Sort: valid articles first, by pub date desc if parseable
        def sort_key(a):
            if a.get("error"):
                return ""
            try:
                from email.utils import parsedate_to_datetime
                return parsedate_to_datetime(a["pub"]).isoformat()
            except Exception:
                return a["pub"]
        articles.sort(key=sort_key, reverse=True)
        self._json({"articles": articles, "fetched_at": datetime.now(timezone.utc).isoformat()})

    # ── POST /route, /upload, /save ──────────────────────────────────────────
    def do_POST(self):
        if self.path == "/route":
            self._handle_route()
        elif self.path == "/upload":
            self._handle_upload()
        elif self.path == "/save":
            self._handle_save()
        elif self.path == "/chat":
            self._handle_chat()
        else:
            self.send_error(404, "Not found")

    def _handle_route(self):
        """
        Classify a PDF without filing it.
        Returns: {success, domain, reason, confidence, custodian, doc_type, fallback, filename}
        The caller can then POST /upload with domain_override to commit the filing.
        """
        ct = self.headers.get("Content-Type", "")
        if "boundary=" not in ct:
            return self._json({"success": False, "error": "Missing multipart boundary"}, 400)

        boundary = ct.split("boundary=", 1)[1].strip()
        length   = int(self.headers.get("Content-Length", 0))
        body     = self.rfile.read(length)
        parts    = _parse_multipart(body, boundary)

        if "file" not in parts or not isinstance(parts["file"], dict):
            return self._json({"success": False, "error": "No file received"}, 400)

        file_info = parts["file"]
        suffix    = Path(file_info.get("filename", "upload.pdf")).suffix or ".pdf"

        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tf:
            tf.write(file_info["data"])
            tmp_path = tf.name

        try:
            proc = subprocess.run(
                [sys.executable, str(SCRIPTS_DIR / "route_document.py"), tmp_path],
                capture_output=True, text=True,
                cwd=str(PROJECT_DIR), timeout=45
            )
            for line in proc.stdout.splitlines():
                if line.startswith("__ROUTE_RESULT__:"):
                    data = json.loads(line[len("__ROUTE_RESULT__:"):])
                    return self._json({"success": True, **data})
            err = (proc.stderr or proc.stdout or "Classifier returned no result").strip()
            return self._json({"success": False, "error": err})

        except subprocess.TimeoutExpired:
            return self._json({"success": False, "error": "Classification timed out (45 s)"})
        except Exception as exc:
            return self._json({"success": False, "error": str(exc)})
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    def _handle_save(self):
        """Save an uploaded file directly to the uploads/ directory and return its URL."""
        ct = self.headers.get("Content-Type", "")
        if "boundary=" not in ct:
            return self._json({"success": False, "error": "Missing multipart boundary"}, 400)
        boundary = ct.split("boundary=", 1)[1].strip()
        length   = int(self.headers.get("Content-Length", 0))
        body     = self.rfile.read(length)
        parts    = _parse_multipart(body, boundary)
        if "file" not in parts or not isinstance(parts["file"], dict):
            return self._json({"success": False, "error": "No file received"}, 400)
        file_info = parts["file"]
        original  = file_info.get("filename", "upload.pdf")
        domain    = parts.get("domain", "general") if isinstance(parts.get("domain"), str) else "general"
        # Sanitise filename and make unique if needed
        safe_name = re.sub(r"[^\w.\-]", "_", original)
        dest = UPLOADS_DIR / safe_name
        counter = 1
        while dest.exists():
            stem, suffix = Path(safe_name).stem, Path(safe_name).suffix
            dest = UPLOADS_DIR / f"{stem}_{counter}{suffix}"
            counter += 1
        dest.write_bytes(file_info["data"])
        self._json({
            "success":  True,
            "filename": dest.name,
            "url":      f"/uploads/{dest.name}",
            "domain":   domain,
            "size":     len(file_info["data"]),
        })

    def _handle_upload(self):
        ct = self.headers.get("Content-Type", "")
        if "boundary=" not in ct:
            return self._json({"success": False, "error": "Missing multipart boundary"}, 400)

        boundary = ct.split("boundary=", 1)[1].strip()
        length   = int(self.headers.get("Content-Length", 0))
        body     = self.rfile.read(length)
        parts    = _parse_multipart(body, boundary)

        if "file" not in parts or not isinstance(parts["file"], dict):
            return self._json({"success": False, "error": "No file received in request"}, 400)

        file_info     = parts["file"]
        suffix        = Path(file_info.get("filename", "upload.pdf")).suffix or ".pdf"
        # Optional: caller can specify the domain (from AI routing + possible override)
        domain_override = parts.get("domain_override", "")
        routing_reason  = parts.get("routing_reason", "")
        if not isinstance(domain_override, str):
            domain_override = ""
        if not isinstance(routing_reason, str):
            routing_reason = ""

        # Also persist the PDF to uploads/ so it stays viewable after import
        original_name = file_info.get("filename", "upload.pdf")
        stem = re.sub(r"[^\w\-.]", "_", Path(original_name).stem)
        ts   = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        dest_name = f"{stem}_{ts}{suffix}"
        dest_path = UPLOADS_DIR / dest_name
        dest_path.write_bytes(file_info["data"])

        # Save to temp path on disk for the import script
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tf:
            tf.write(file_info["data"])
            tmp_path = tf.name

        try:
            cmd = [sys.executable, str(SCRIPTS_DIR / "import_statement.py"), tmp_path]
            if domain_override:
                cmd += ["--domain-override", domain_override]
            if routing_reason:
                cmd += ["--routing-reason", routing_reason]

            proc = subprocess.run(
                cmd,
                capture_output=True, text=True,
                cwd=str(PROJECT_DIR), timeout=60
            )
            # import_statement.py prints a line starting with __IMPORT_RESULT__:
            for line in proc.stdout.splitlines():
                if line.startswith("__IMPORT_RESULT__:"):
                    data = json.loads(line[len("__IMPORT_RESULT__:"):])
                    pdf_url = f"/uploads/{dest_name}"
                    data["pdfUrl"] = pdf_url
                    # Patch the registry so the pdfUrl is persisted and shows up in the dashboard
                    _patch_registry_pdf_url(data.get("id"), pdf_url)
                    return self._json(data)
            # No JSON token found — return stderr for debugging
            err = proc.stderr.strip() or proc.stdout.strip() or "Import returned no result"
            return self._json({"success": False, "error": err})

        except subprocess.TimeoutExpired:
            return self._json({"success": False, "error": "Import timed out (60 s)"})
        except Exception as exc:
            return self._json({"success": False, "error": str(exc)})
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    # ── AI chat ──────────────────────────────────────────────────────────────
    def _handle_chat(self):
        """
        POST /chat  { "message": "...", "history": [...] }
        Calls Claude with a system prompt built from the live archive.
        Returns { "reply": "..." }
        """
        length = int(self.headers.get("Content-Length", 0))
        body   = self.rfile.read(length)
        try:
            payload = json.loads(body)
        except Exception:
            return self._json({"error": "Invalid JSON"}, 400)

        user_message = payload.get("message", "").strip()
        history      = payload.get("history", [])   # [{role,content}, …]
        if not user_message:
            return self._json({"error": "Empty message"}, 400)

        api_key = _load_api_key_standalone()
        if not api_key:
            return self._json({"reply": (
                "The AI assistant is not yet connected. To enable it, add your Anthropic API key "
                "to a .env file in the project root:\n\nANTHROPIC_API_KEY=sk-ant-..."
            )})

        # Build archive context (read up to ~60 KB of records)
        archive_context = _build_archive_context(PROJECT_DIR / "archive")

        system_prompt = f"""You are the Smith Family Office AI Assistant, embedded in the family's private wealth-management platform.

You have access to the family's full archive, excerpted below. Use it to answer questions precisely. When quoting figures or facts, cite the source record name. Keep answers clear and concise — the family includes members without a finance background, so explain jargon when it appears.

Tone: warm, professional, authoritative. Never speculate beyond what the archive contains. If something isn't in the archive, say so plainly and suggest where the family might look.

=== ARCHIVE CONTEXT ===
{archive_context}
=== END ARCHIVE CONTEXT ==="""

        try:
            try:
                import anthropic
            except ImportError:
                import subprocess as _sp, sys as _sys
                _sp.run([_sys.executable, "-m", "pip", "install", "anthropic", "--quiet", "--break-system-packages"], check=True)
                import anthropic

            client = anthropic.Anthropic(api_key=api_key)

            messages = []
            # Carry forward conversation history (last 10 turns max)
            for turn in history[-10:]:
                role    = turn.get("role", "")
                content = turn.get("content", "")
                if role in ("user", "assistant") and content:
                    messages.append({"role": role, "content": content})
            messages.append({"role": "user", "content": user_message})

            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                system=system_prompt,
                messages=messages,
            )
            reply = response.content[0].text if response.content else "No response."
            return self._json({"reply": reply})

        except Exception as exc:
            return self._json({"reply": f"Error contacting AI: {exc}"})

    # ── helpers ────────────────────────────────────────────────────────────────────────────────────
    def _json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self._cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def _cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def log_message(self, fmt, *args):
        code = str(args[1]) if len(args) > 1 else ""
        path = str(args[0]) if args else ""
        if "/upload" in path or "/route" in path or (code and code not in ("200", "304", "204")):
            import sys as _sys
            _sys.stderr.write("[%s] %s\n" % (self.address_string(), fmt % args))


REGISTRY_PATH = PROJECT_DIR / "ops-dashboard-demo" / "src" / "data" / "imports-registry.json"


def _load_api_key_standalone() -> str:
    """Load ANTHROPIC_API_KEY from environment or .env file."""
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if key:
        return key
    for env_file in (PROJECT_DIR / ".env", PROJECT_DIR / "scripts" / ".env"):
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
                line = line.strip()
                if line.startswith("ANTHROPIC_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def _build_archive_context(archive_dir, max_bytes=60_000):
    """
    Walk archive/ and concatenate .md file contents up to max_bytes.
    Returns a single string used as context in the chat system prompt.
    """
    from pathlib import Path as _Path
    archive_dir = _Path(archive_dir)
    if not archive_dir.exists():
        return "(No archive records found.)"

    chunks = []
    total  = 0
    for md_file in sorted(archive_dir.rglob("*.md")):
        if "_archived" in md_file.parts or md_file.name.startswith("_"):
            continue
        try:
            text = md_file.read_text(encoding="utf-8", errors="ignore").strip()
        except OSError:
            continue
        if not text:
            continue
        rel = md_file.relative_to(archive_dir)
        header = f"\n\n--- {rel} ---\n"
        snippet = header + text
        if total + len(snippet) > max_bytes:
            remaining = max_bytes - total
            if remaining > len(header) + 200:
                chunks.append(snippet[:remaining] + "\n… [truncated]")
            break
        chunks.append(snippet)
        total += len(snippet)

    return "".join(chunks) if chunks else "(Archive is empty.)"


def _patch_registry_pdf_url(import_id: str, pdf_url: str):
    """Write pdfUrl back into the registry entry so the dashboard can link to the PDF."""
    if not import_id or not REGISTRY_PATH.exists():
        return
    try:
        registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        patched  = False
        for entry in registry:
            if entry.get("id") == import_id and not entry.get("pdfUrl"):
                entry["pdfUrl"] = pdf_url
                patched = True
        if patched:
            REGISTRY_PATH.write_text(json.dumps(registry, indent=2), encoding="utf-8")
    except Exception as exc:
        import sys as _sys
        _sys.stderr.write(f"[server] registry patch failed: {exc}\n")


def _parse_multipart(body: bytes, boundary: str) -> dict:
    sep    = ("--" + boundary).encode()
    result = {}
    for part in body.split(sep)[1:]:
        if part.strip() in (b"--", b"--\r\n", b""):
            continue
        if b"\r\n\r\n" not in part:
            continue
        hdr_bytes, content = part.split(b"\r\n\r\n", 1)
        if content.endswith(b"\r\n"):
            content = content[:-2]
        hdr  = hdr_bytes.decode("utf-8", errors="replace")
        nm   = re.search(r'name="([^"]+)"', hdr)
        fm   = re.search(r'filename="([^"]*)"', hdr)
        if nm:
            name = nm.group(1)
            if fm:
                result[name] = {"filename": fm.group(1), "data": content}
            else:
                result[name] = content.decode("utf-8", errors="replace")
    return result


if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), FamilyOfficeHandler) as httpd:
        print(f"\u2713 Family Office Platform running at http://localhost:{PORT}")
        print(f"  Serving: {DIST_DIR}")
        print(f"  Project: {PROJECT_DIR}")
        httpd.serve_forever()