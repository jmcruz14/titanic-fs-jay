from functools import lru_cache
from typing import Dict, Optional, Annotated, Any
from fastapi import APIRouter, Query, Depends, Request, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, ProgrammingError

from .dbconnect import get_db, SessionLocal
from .api_utils import limiter
from .db_models import Passenger
from .models import PassengerSex, Pclass, Embarked

router = APIRouter()

@lru_cache(maxsize=128)
def get_cached_summary():
    """Cache summary since data is static"""
    db = SessionLocal()
    try:

      total = db.query(func.count(Passenger.passenger_id)).scalar()
      survived = db.query(func.count(Passenger.passenger_id)).filter(
          Passenger.survived
      ).scalar()
      db.close()
      
      return {
          "total_passengers": total,
          "survived": survived,
          "died": total - survived,
          "survival_rate": round(survived / total, 4) if total > 0 else 0.0
      }
    
    except (IntegrityError, ProgrammingError) as e:
      # Database-related errors
      raise HTTPException(
          status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
          detail=f"Database error during import: {str(e)}"
      )
    except Exception as e:
        # Catch-all for unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during import: {str(e)}"
        )


@router.get("/passenger/{passenger_id}")
@limiter.limit("10/minute")
async def get_individual_passenger(
    request: Request, 
    passenger_id: int,
    db: Session = Depends(get_db)
):
    """Get a single passenger by PassengerId"""

    try:
      passenger = db.query(Passenger).filter(
          Passenger.passenger_id == passenger_id
      ).first()
      
      if not passenger:
          raise HTTPException(
              status_code=status.HTTP_404_NOT_FOUND,
              detail="Passenger not found"
          )
      
      return {
          "passenger_id": passenger.passenger_id,
          "survived": passenger.survived,
          "pclass": passenger.pclass,
          "name": passenger.name,
          "sex": passenger.sex,
          "age": passenger.age,
          "sibsp": passenger.sibsp,
          "parch": passenger.parch,
          "ticket": passenger.ticket,
          "fare": passenger.fare,
          "cabin": passenger.cabin,
          "embarked": passenger.embarked
      }
    except (IntegrityError, ProgrammingError) as e:
      # Database-related errors
      raise HTTPException(
          status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
          detail=f"Database error during import: {str(e)}"
      )
    except Exception as e:
      # Catch-all for unexpected errors
      raise HTTPException(
          status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
          detail=f"Unexpected error during import: {str(e)}"
      )

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
    page_size: int = Query(100, ge=1, le=100, description="Results per page"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get passengers with optional filters and pagination"""

    try:
    
      # Build query with filters
      query = db.query(Passenger)
      
      if survived is not None:
          query = query.filter(Passenger.survived == bool(survived))
      if sex is not None:
          query = query.filter(Passenger.sex == sex.value)
      if pclass is not None:
          query = query.filter(Passenger.pclass == pclass.value)
      if sibsp is not None:
          query = query.filter(Passenger.sibsp == sibsp)
      if parch is not None:
          query = query.filter(Passenger.parch == parch)
      if embarked is not None:
          query = query.filter(Passenger.embarked == embarked.value)
      
      # Get total count
      total_count = query.count()
      total_pages = (total_count + page_size - 1) // page_size
      
      # Apply pagination
      offset = (page - 1) * page_size
      passengers = query.offset(offset).limit(page_size).all()
      
      return {
          "count": total_count,
          "page": page,
          "page_size": page_size,
          "total_pages": total_pages,
          "returned": len(passengers),
          "passengers": [
              {
                  "passenger_id": p.passenger_id,
                  "survived": p.survived,
                  "pclass": p.pclass,
                  "name": p.name,
                  "sex": p.sex,
                  "age": p.age,
                  "sibsp": p.sibsp,
                  "parch": p.parch,
                  "ticket": p.ticket,
                  "fare": p.fare,
                  "cabin": p.cabin,
                  "embarked": p.embarked
              }
              for p in passengers
          ]
      }
    
    except (ProgrammingError) as e:
      # Database-related errors
      raise HTTPException(
          status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
          detail=f"Database error during import: {str(e)}"
      )
    
    except (IntegrityError):
       raise HTTPException(
          status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
          detail="'passengers' table has not yet been created. Import the titanic dataset first."
       )

    except Exception as e:
        # Catch-all for unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during import: {str(e)}"
        )

@router.get("/passengers/summary")
@limiter.limit("10/minute")
async def get_summary(request: Request) -> Dict:
    return get_cached_summary()