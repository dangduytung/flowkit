"""Backward-compatible import path; the implementation lives in tools.common.product."""
from tools.common.product import ProductInfo, parse_description, parse_product_zip

__all__ = ["ProductInfo", "parse_description", "parse_product_zip"]
