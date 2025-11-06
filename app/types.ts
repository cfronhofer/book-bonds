export interface CompatibilityMetrics {
  person1_books_finished: number;
  person2_books_finished: number;
  shared_books_finished: number;
  shared_authors: number;
  cross_recommendations: number;
  shared_tbr: number;
  disagreements: number;
}

export interface SharedAuthor {
  author: string;
  person1_count: number;
  person2_count: number;
  total: number;
}

export interface ScoreBreakdown {
  shared_finished: number;
  shared_authors: number;
  cross_recommendations: number;
  shared_tbr: number;
  reading_behavior: number;
  disagreement_penalty: number;
}

export interface CompatibilityResult {
  person1: string;
  person2: string;
  compatibility_score: number;
  metrics: CompatibilityMetrics;
  top_shared_books: string[];
  top_shared_authors: SharedAuthor[];
  shared_tbr_sample: string[];
  diagnosis: string;
  score_breakdown: ScoreBreakdown;
}

export interface CompatibilityData {
  metadata: {
    generated_at: string;
    total_pairings: number;
    average_compatibility: number;
  };
  results: CompatibilityResult[];
}
