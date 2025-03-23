class ScanTarget:
    def __init__(self, url, scan_type, scope=None, exclude=None, options=None, templates=None):
        self.url = url
        self.scan_type = scan_type
        self.scope = scope if scope is not None else []
        self.exclude = exclude if exclude is not None else []
        self.options = options if options is not None else {}
        self.templates = templates if templates is not None else []

    def __repr__(self):
        return f"<ScanTarget(url={self.url}, scan_type={self.scan_type})>"
