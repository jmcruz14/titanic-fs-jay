import polars as pl
from pathlib import Path
from typing import Dict, List, Optional, Annotated, Any
from fastapi import APIRouter, Query, Request, HTTPException, status

from .api_utils import limiter
from .models import PassengerSex, Pclass, Embarked

DATA_PATH = Path(__file__).parent.parent / "data" / "titanic.csv"
df = pl.read_csv(DATA_PATH)

router = APIRouter()

@router.get("/passenger/{passenger_id}")
@limiter.limit("10/minute")
async def get_individual_passenger(request: Request, passenger_id: int = 1):
  """Get a single passenger by PassengerId"""
  passenger = df.filter(pl.col("PassengerId") == passenger_id)
    
  if passenger.height == 0: 
      raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Passenger not found"
        )

  return passenger.row(0, named=True)

@router.get("/passengers")
@limiter.limit("10/minute")
async def get_passengers(
  request: Request,
  survived: Annotated[int | None, Query(ge=0, le=1, description="Filter by survival status")] = None,
  sex: Optional[PassengerSex] = Query(None, description="Filter by gender"),
  pclass: Optional[Pclass] = Query(None, description="Filter by passenger class (1, 2, or 3)"),
  sibsp: Optional[int] = Query(None, ge=0, description="Filter by number of siblings/spouses"),
  parch: Optional[int] = Query(None, ge=0, description="Filter by number of parents/children"),
  embarked: Optional[Embarked] = Query(None, description="Filter by port of embarkation"),
  page: int = Query(1, ge=1, description="Page number (1-indexed)"),
  page_size: int = Query(100, ge=1, le=1000, description="Results per page")
) -> Dict[str, Any]:
  
  filtered_df = df
  # Apply filters using Polars expressions
  if survived is not None:
      filtered_df = filtered_df.filter(pl.col("Survived") == int(survived))
  if sex is not None:
        filtered_df = filtered_df.filter(pl.col("Sex") == sex.value)
  if pclass is not None:
      filtered_df = filtered_df.filter(pl.col("Pclass") == pclass.value)
  if sibsp is not None:
      filtered_df = filtered_df.filter(pl.col("SibSp") == sibsp)
  if parch is not None:
      filtered_df = filtered_df.filter(pl.col("Parch") == parch)
  if embarked is not None:
      filtered_df = filtered_df.filter(pl.col("Embarked") == embarked.value)

  # Pagination
  total_count = filtered_df.height
  total_pages = (total_count + page_size - 1) // page_size
  offset = (page - 1) * page_size
  result_df = filtered_df.slice(offset, page_size)

  return {
    "count": total_count,
    "page": page,
    "page_size": page_size,
    "total_pages": total_pages,
    "returned": result_df.height,
    "passengers": result_df.to_dicts()
  }

@router.get("/passengers/summary")
@limiter.limit("10/minute")
def get_summary(request: Request) -> Dict:
    return {
        "total_passengers": df.height,
        "survived": int(df["Survived"].sum()),
        "died": int((df["Survived"] == 0).sum()),
        "survival_rate": float(df["Survived"].mean()),
    }


# NOTE: could be useful to implement for the frontend
# @router.get("/api/age-distribution")
# def age_distribution() -> List[Dict]:
#     age_bins = [0, 12, 18, 35, 50, 100]
#     labels = ['Child', 'Teen', 'Young Adult', 'Adult', 'Senior']
    
#     result = (
#         df.filter(pl.col("Age").is_not_null())
#         .with_columns(
#             pl.col("Age").cut(age_bins, labels=labels).alias("AgeGroup")
#         )
#         .group_by("AgeGroup")
#         .agg([
#             pl.col("Survived").sum().alias("survived"),
#             pl.col("Survived").count().alias("total"),
#             pl.col("Survived").mean().alias("rate")
#         ])
#     )
#     return [
#         {
#             "age_group": str(row["AgeGroup"]),
#             "survived": int(row["survived"]),
#             "total": int(row["total"]),
#             "rate": float(row["rate"])
#         }
#         for row in result.iter_rows(named=True)
#  ]

# ????
# @router.get("/api/fare-analysis")
# def fare_analysis() -> List[Dict]:
#     fare_bins = [0, 10, 30, 100, 600]
#     labels = ['Low', 'Medium', 'High', 'Very High']
    
#     result = (
#         df.filter(pl.col("Fare").is_not_null())
#         .with_columns(
#             pl.col("Fare").cut(fare_bins, labels=labels).alias("FareGroup")
#         )
#         .group_by("FareGroup")
#         .agg([
#             pl.col("Survived").sum().alias("survived"),
#             pl.col("Survived").count().alias("total"),
#             pl.col("Survived").mean().alias("rate")
#         ])
#     )
#     return [
#         {
#             "fare_group": str(row["FareGroup"]),
#             "survived": int(row["survived"]),
#             "total": int(row["total"]),
#             "rate": float(row["rate"])
#         }
#         for row in result.iter_rows(named=True)
#     ]