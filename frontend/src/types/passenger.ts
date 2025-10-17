export interface Passenger {
  PassengerId: number;
  Survived: number;
  Pclass: number;
  Name: string;
  Sex: 'male' | 'female';
  Age: number | null;
  SibSp: number;
  Parch: number;
  Ticket: string;
  Fare: number;
  Cabin: string | null;
  Embarked: 'C' | 'Q' | 'S' | null;
}

export interface PaginatedResponse {
  count: number;
  page: number;
  page_size: number;
  total_pages: number;
  returned: number;
  passengers: Passenger[];
}

export interface Filters {
  survived?: number;
  sex?: string;
  pclass?: number;
  sibsp?: number;
  parch?: number;
  embarked?: string;
}

export interface Summary {
  total_passengers: number;
  survived: number;
  died: number;
  survival_rate: number;
}
