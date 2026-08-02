from typing import List
from sqlalchemy.orm import Session

from app.models.complaint import Complaint


def find_possible_duplicates(db: Session, extracted: dict, lookback_days: int = 90) -> List[Complaint]:
    """
    Lightweight duplicate detection: flags existing complaints that share the same
    batch/lot number AND product name (the two fields most indicative of the same
    underlying quality event). Good enough for a demo; a production version would
    add embedding similarity over detailed_description.
    """
    batch = extracted.get("batch_lot_number")
    product = extracted.get("product_name")

    if not batch and not product:
        return []

    query = db.query(Complaint)
    if batch:
        query = query.filter(Complaint.batch_lot_number == batch)
    if product:
        query = query.filter(Complaint.product_name == product)

    return query.all()
