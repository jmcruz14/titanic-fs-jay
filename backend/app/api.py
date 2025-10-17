import polars as pl
from pathlib import Path
from typing import Dict, List
from fastapi import APIRouter

DATA_PATH = Path(__file__).parent.parent / "data" / "titanic.csv"
df = pl.read_csv(DATA_PATH)

router = APIRouter()

@router.get("/api/summary")
def get_summary() -> Dict:
    return {
        "total_passengers": df.height,
        "survived": int(df["Survived"].sum()),
        "died": int((df["Survived"] == 0).sum()),
        "survival_rate": float(df["Survived"].mean()),
    }

@router.get("/api/survival-by-class")
def survival_by_class() -> List[Dict]:
    result = (
        df.group_by("Pclass")
        .agg([
            pl.col("Survived").sum().alias("survived"),
            pl.col("Survived").count().alias("total"),
            pl.col("Survived").mean().alias("rate")
        ])
        .sort("Pclass")
    )
    return [
        {
            "class": int(row["Pclass"]),
            "survived": int(row["survived"]),
            "total": int(row["total"]),
            "rate": float(row["rate"])
        }
        for row in result.iter_rows(named=True)
    ]

@router.get("/api/survival-by-gender")
def survival_by_gender() -> List[Dict]:
    result = (
        df.group_by("Sex")
        .agg([
            pl.col("Survived").sum().alias("survived"),
            pl.col("Survived").count().alias("total"),
            pl.col("Survived").mean().alias("rate")
        ])
    )
    return [
        {
            "gender": row["Sex"],
            "survived": int(row["survived"]),
            "total": int(row["total"]),
            "rate": float(row["rate"])
        }
        for row in result.iter_rows(named=True)
    ]

@router.get("/api/age-distribution")
def age_distribution() -> List[Dict]:
    age_bins = [0, 12, 18, 35, 50, 100]
    labels = ['Child', 'Teen', 'Young Adult', 'Adult', 'Senior']
    
    result = (
        df.filter(pl.col("Age").is_not_null())
        .with_columns(
            pl.col("Age").cut(age_bins, labels=labels).alias("AgeGroup")
        )
        .group_by("AgeGroup")
        .agg([
            pl.col("Survived").sum().alias("survived"),
            pl.col("Survived").count().alias("total"),
            pl.col("Survived").mean().alias("rate")
        ])
    )
    return [
        {
            "age_group": str(row["AgeGroup"]),
            "survived": int(row["survived"]),
            "total": int(row["total"]),
            "rate": float(row["rate"])
        }
        for row in result.iter_rows(named=True)
    ]

@router.get("/api/fare-analysis")
def fare_analysis() -> List[Dict]:
    fare_bins = [0, 10, 30, 100, 600]
    labels = ['Low', 'Medium', 'High', 'Very High']
    
    result = (
        df.filter(pl.col("Fare").is_not_null())
        .with_columns(
            pl.col("Fare").cut(fare_bins, labels=labels).alias("FareGroup")
        )
        .group_by("FareGroup")
        .agg([
            pl.col("Survived").sum().alias("survived"),
            pl.col("Survived").count().alias("total"),
            pl.col("Survived").mean().alias("rate")
        ])
    )
    return [
        {
            "fare_group": str(row["FareGroup"]),
            "survived": int(row["survived"]),
            "total": int(row["total"]),
            "rate": float(row["rate"])
        }
        for row in result.iter_rows(named=True)
    ]