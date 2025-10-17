import polars as pl
from pathlib import Path
from fastapi import APIRouter, Request, HTTPException, status
from sqlalchemy.exc import IntegrityError, ProgrammingError

from .dbconnect import engine
from .api_utils import limiter
from .db_models import Base

csv_router = APIRouter()

@csv_router.post("/import/titanic", tags=['import_csv'])
@limiter.limit("5/minute")
async def import_titanic_csv(request: Request):
  """Imports Titanic CSV data into instantiated Postgres Database"""
    
  try:
      # Create tables if they don't exist
      Base.metadata.create_all(bind=engine)
      
      # Load CSV
      DATA_PATH = Path(__file__).parent.parent / "data" / "titanic.csv"
      
      if not DATA_PATH.exists():
          raise HTTPException(
              status_code=status.HTTP_404_NOT_FOUND,
              detail=f"CSV file not found at {DATA_PATH}"
          )
      
      df = pl.read_csv(DATA_PATH)
      
      # Rename columns
      df = df.rename({
          'PassengerId': 'passenger_id',
          'Survived': 'survived',
          'Pclass': 'pclass',
          'Name': 'name',
          'Sex': 'sex',
          'Age': 'age',
          'SibSp': 'sibsp',
          'Parch': 'parch',
          'Ticket': 'ticket',
          'Fare': 'fare',
          'Cabin': 'cabin',
          'Embarked': 'embarked'
      })
      
      # Write to database
      rows_written = df.write_database(
          table_name="passengers",
          connection=engine,
          engine='sqlalchemy',
          engine_options={
              "if_exists": "fail",  # Raises error if table exists
              "method": "multi"
          }
      )
      
      print(f"✅ {rows_written} rows successfully added to 'passengers' table")
      
      return {
          "updated_rows": rows_written,
          "message": "Import successful"
      }
      
  except ValueError as e:
      # Triggered when table already exists with if_exists="fail"
      raise HTTPException(
          status_code=status.HTTP_409_CONFLICT,
          detail=f"Table 'passengers' already exists. Use DELETE endpoint to clear before re-importing. Error: {str(e)}"
      )
  
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
