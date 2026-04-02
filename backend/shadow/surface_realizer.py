class SurfaceRealizer:
    """
    Converts structured runtime content → natural language.
    No reasoning. No world modeling.
    """

    def to_text(self, content_struct):
        if isinstance(content_struct, str):
            return content_struct

        if isinstance(content_struct, dict):
            # Basic structured content format:
            # { "type": "text", "value": "..." }
            if content_struct.get("type") == "text":
                return content_struct.get("value", "")

        # Fallback
        return str(content_struct)
