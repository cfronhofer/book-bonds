#!/usr/bin/env python3
"""
Batch Reading Compatibility Analyzer
Processes all possible pairings from multiple reading lists and outputs structured results
"""

import pandas as pd
import numpy as np
from collections import defaultdict, Counter
import json
import re
from pathlib import Path
from itertools import combinations
from datetime import datetime
import sys

class ReadingCompatibilityAnalyzer:
    def __init__(self):
        self.results = []
        
    def normalize_title(self, title):
        """Normalize book titles for comparison"""
        if pd.isna(title):
            return ""
        title = re.sub(r'[^\w\s]', '', str(title).lower())
        return ' '.join(title.split())
    
    def get_primary_author(self, author_str):
        """Extract primary author from author string"""
        if pd.isna(author_str):
            return ""
        authors = str(author_str).split('+')
        return authors[0].strip().lower() if authors else ""
    
    def calculate_compatibility(self, person1_name, person1_df, person2_name, person2_df):
        """Calculate compatibility score between two people"""
        
        # Filter out deleted entries
        df1 = person1_df[person1_df['Status'] != 'deleted'].copy()
        df2 = person2_df[person2_df['Status'] != 'deleted'].copy()
        
        # Normalize titles and authors
        df1['normalized_title'] = df1['Title'].apply(self.normalize_title)
        df2['normalized_title'] = df2['Title'].apply(self.normalize_title)
        df1['primary_author'] = df1['Author'].apply(self.get_primary_author)
        df2['primary_author'] = df2['Author'].apply(self.get_primary_author)
        
        # Create status-based sets
        # Include both 'finished' and 'currently_reading' in the finished category
        books1 = {
            'finished': set(df1[df1['Status'].isin(['finished', 'currently_reading'])]['normalized_title']),
            'want_to_read': set(df1[df1['Status'] == 'want_to_read']['normalized_title']),
            'did_not_finish': set(df1[df1['Status'] == 'did_not_finish']['normalized_title']),
            'all': set(df1['normalized_title'])
        }

        books2 = {
            'finished': set(df2[df2['Status'].isin(['finished', 'currently_reading'])]['normalized_title']),
            'want_to_read': set(df2[df2['Status'] == 'want_to_read']['normalized_title']),
            'did_not_finish': set(df2[df2['Status'] == 'did_not_finish']['normalized_title']),
            'all': set(df2['normalized_title'])
        }

        authors1 = {
            'finished': set(df1[df1['Status'].isin(['finished', 'currently_reading'])]['primary_author']) - {''},
            'all': set(df1['primary_author']) - {''}
        }

        authors2 = {
            'finished': set(df2[df2['Status'].isin(['finished', 'currently_reading'])]['primary_author']) - {''},
            'all': set(df2['primary_author']) - {''}
        }
        
        # Calculate overlaps
        shared_finished = books1['finished'] & books2['finished']
        shared_tbr = books1['want_to_read'] & books2['want_to_read']
        p1_read_p2_wants = books1['finished'] & books2['want_to_read']
        p2_read_p1_wants = books2['finished'] & books1['want_to_read']
        shared_dnf = books1['did_not_finish'] & books2['did_not_finish']
        p1_finished_p2_dnf = books1['finished'] & books2['did_not_finish']
        p2_finished_p1_dnf = books2['finished'] & books1['did_not_finish']
        
        shared_authors_finished = authors1['finished'] & authors2['finished']
        shared_authors_all = authors1['all'] & authors2['all']
        
        # Calculate scores
        scores = {}
        
        # 1. Shared finished books (35%)
        if len(books1['finished']) + len(books2['finished']) > 0:
            shared_finished_score = len(shared_finished) / min(len(books1['finished']), len(books2['finished'])) if min(len(books1['finished']), len(books2['finished'])) > 0 else 0
            scores['shared_finished'] = min(1.0, shared_finished_score) * 0.35
        else:
            scores['shared_finished'] = 0
            
        # 2. Shared authors (30%)
        if len(authors1['all']) + len(authors2['all']) > 0:
            author_jaccard = len(shared_authors_all) / len(authors1['all'] | authors2['all'])
            scores['shared_authors'] = np.sqrt(author_jaccard) * 0.30
        else:
            scores['shared_authors'] = 0
            
        # 3. Cross-recommendations (10%)
        total_possible = len(books1['finished']) + len(books2['finished'])
        if total_possible > 0:
            cross_rec_score = (len(p1_read_p2_wants) + len(p2_read_p1_wants)) / (total_possible * 0.1)
            scores['cross_recommendations'] = min(1.0, cross_rec_score) * 0.10
        else:
            scores['cross_recommendations'] = 0
            
        # 4. Shared TBR (20%)
        if len(books1['want_to_read']) + len(books2['want_to_read']) > 0:
            tbr_jaccard = len(shared_tbr) / len(books1['want_to_read'] | books2['want_to_read'])
            scores['shared_tbr'] = tbr_jaccard * 0.20
        else:
            scores['shared_tbr'] = 0
            
        # 5. Reading behavior (5%)
        p1_finish_rate = len(books1['finished']) / len(books1['all']) if len(books1['all']) > 0 else 0
        p2_finish_rate = len(books2['finished']) / len(books2['all']) if len(books2['all']) > 0 else 0
        finish_rate_similarity = 1 - abs(p1_finish_rate - p2_finish_rate)
        size_ratio = min(len(books1['all']), len(books2['all'])) / max(len(books1['all']), len(books2['all'])) if max(len(books1['all']), len(books2['all'])) > 0 else 0
        scores['reading_behavior'] = (finish_rate_similarity * 0.7 + size_ratio * 0.3) * 0.05
        
        # 6. Disagreement penalty
        disagreements = len(p1_finished_p2_dnf) + len(p2_finished_p1_dnf)
        scores['disagreement_penalty'] = -min(0.15, disagreements * 0.02)
        
        total_score = sum(scores.values())
        
        # Get top shared authors with counts
        shared_author_counts = []
        if shared_authors_finished:
            p1_finished = df1[df1['Status'].isin(['finished', 'currently_reading'])]
            p2_finished = df2[df2['Status'].isin(['finished', 'currently_reading'])]

            for author in shared_authors_finished:
                p1_count = len(p1_finished[p1_finished['primary_author'] == author])
                p2_count = len(p2_finished[p2_finished['primary_author'] == author])
                shared_author_counts.append({
                    'author': author.title(),
                    'person1_count': p1_count,
                    'person2_count': p2_count,
                    'total': p1_count + p2_count
                })

            shared_author_counts.sort(key=lambda x: x['total'], reverse=True)
        
        # Generate diagnosis
        diagnosis = self.generate_diagnosis(
            total_score,
            len(books1['finished']),
            len(books2['finished']),
            len(shared_finished),
            len(shared_authors_finished),
            len(p1_read_p2_wants) + len(p2_read_p1_wants),
            disagreements
        )
        
        # Convert sets to lists for JSON serialization
        shared_finished_list = list(shared_finished)[:10]  # Top 10
        shared_tbr_list = list(shared_tbr)[:5]
        
        return {
            'person1': person1_name,
            'person2': person2_name,
            'compatibility_score': round(total_score * 100, 1),
            'metrics': {
                'person1_books_finished': len(books1['finished']),
                'person2_books_finished': len(books2['finished']),
                'shared_books_finished': len(shared_finished),
                'shared_authors': len(shared_authors_finished),
                'cross_recommendations': len(p1_read_p2_wants) + len(p2_read_p1_wants),
                'shared_tbr': len(shared_tbr),
                'disagreements': disagreements
            },
            'top_shared_books': shared_finished_list,
            'top_shared_authors': shared_author_counts[:5],
            'shared_tbr_sample': shared_tbr_list,
            'diagnosis': diagnosis,
            'score_breakdown': {k: round(v, 3) for k, v in scores.items()}
        }
    
    def generate_diagnosis(self, score, p1_finished, p2_finished, shared_finished, shared_authors, cross_recs, disagreements):
        """Generate qualitative diagnosis text"""
        
        # Determine compatibility level
        if score >= 0.70:
            level = "EXCELLENT"
            emoji = "🌟"
        elif score >= 0.50:
            level = "GOOD"
            emoji = "😊"
        elif score >= 0.30:
            level = "MODERATE"
            emoji = "👍"
        elif score >= 0.15:
            level = "LOW"
            emoji = "🤔"
        else:
            level = "MINIMAL"
            emoji = "😅"
        
        # Calculate overlap percentage
        total_unique_finished = len(set(range(p1_finished)) | set(range(p2_finished)))
        overlap_pct = (shared_finished / total_unique_finished * 100) if total_unique_finished > 0 else 0
        
        # Size difference factor
        size_diff = abs(p1_finished - p2_finished)
        size_balanced = size_diff < 20
        
        # Build diagnosis
        diagnosis_parts = []
        
        # Main assessment
        diagnosis_parts.append(f"{emoji} {level} COMPATIBILITY ({score*100:.1f}%)")
        
        # Key insights
        if shared_finished > 10:
            diagnosis_parts.append(f"Strong overlap with {shared_finished} shared books.")
        elif shared_finished > 5:
            diagnosis_parts.append(f"Decent overlap with {shared_finished} shared books.")
        elif shared_finished > 2:
            diagnosis_parts.append(f"Some overlap with {shared_finished} shared books.")
        else:
            diagnosis_parts.append(f"Limited overlap with only {shared_finished} shared books.")
        
        # Size dynamics
        if not size_balanced:
            if p1_finished > p2_finished * 2:
                diagnosis_parts.append("Large library size difference - first reader is much more prolific.")
            elif p2_finished > p1_finished * 2:
                diagnosis_parts.append("Large library size difference - second reader is much more prolific.")
        
        # Recommendations potential
        if cross_recs > 20:
            diagnosis_parts.append(f"Excellent recommendation potential ({cross_recs} books to share).")
        elif cross_recs > 10:
            diagnosis_parts.append(f"Good recommendation potential ({cross_recs} books to share).")
        elif cross_recs > 5:
            diagnosis_parts.append(f"Some recommendation potential ({cross_recs} books to share).")
        
        # Disagreements
        if disagreements > 5:
            diagnosis_parts.append(f"Notable taste differences ({disagreements} disagreements).")
        elif disagreements > 0:
            diagnosis_parts.append(f"Minor taste differences ({disagreements} disagreements).")
        
        # Author overlap
        if shared_authors > 5:
            diagnosis_parts.append(f"Very strong author overlap ({shared_authors} shared).")
        elif shared_authors > 2:
            diagnosis_parts.append(f"Good author overlap ({shared_authors} shared).")
        
        return " ".join(diagnosis_parts)
    
    def process_all_files(self, directory_path):
        """Process all CSV files in directory"""
        
        directory = Path(directory_path)
        csv_files = list(directory.glob("*.csv"))
        
        if len(csv_files) < 2:
            print(f"Error: Need at least 2 CSV files. Found {len(csv_files)}")
            return
        
        print(f"Found {len(csv_files)} reading lists")
        print(f"Will calculate {len(list(combinations(csv_files, 2)))} compatibility scores\n")
        
        # Load all dataframes
        people_data = {}
        for file_path in csv_files:
            # Extract person name from filename (assuming format: Tracked_Books_-_Name.csv)
            name = file_path.stem.replace("Tracked_Books_-_", "").replace("_", " ").strip()
            if not name:
                name = file_path.stem
            
            try:
                df = pd.read_csv(file_path)
                people_data[name] = df
                print(f"✓ Loaded {name}: {len(df)} entries")
            except Exception as e:
                print(f"✗ Error loading {file_path}: {e}")
        
        print(f"\nCalculating compatibility scores...")
        
        # Process all pairs
        for (person1, df1), (person2, df2) in combinations(people_data.items(), 2):
            try:
                result = self.calculate_compatibility(person1, df1, person2, df2)
                self.results.append(result)
                print(f"  {person1} × {person2}: {result['compatibility_score']}%")
            except Exception as e:
                print(f"  Error processing {person1} × {person2}: {e}")
        
        return self.results
    
    def save_results(self, output_path="compatibility_results.json"):
        """Save results to JSON file"""
        
        # Sort by compatibility score
        self.results.sort(key=lambda x: x['compatibility_score'], reverse=True)
        
        output = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_pairings': len(self.results),
                'average_compatibility': round(np.mean([r['compatibility_score'] for r in self.results]), 1)
            },
            'results': self.results
        }
        
        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\nResults saved to {output_path}")
        
    def save_summary_csv(self, output_path="compatibility_summary.csv"):
        """Save summary to CSV for easy viewing"""
        
        summary_data = []
        for result in self.results:
            summary_data.append({
                'Person 1': result['person1'],
                'Person 2': result['person2'],
                'Compatibility %': result['compatibility_score'],
                'Shared Books': result['metrics']['shared_books_finished'],
                'Shared Authors': result['metrics']['shared_authors'],
                'Can Recommend': result['metrics']['cross_recommendations'],
                'Diagnosis': result['diagnosis'].split('.')[0]  # First sentence only
            })
        
        df = pd.DataFrame(summary_data)
        df.to_csv(output_path, index=False)
        print(f"Summary saved to {output_path}")
        
        # Print top 10 matches
        print("\n🏆 TOP 10 MATCHES:")
        for i, row in df.head(10).iterrows():
            print(f"{i+1}. {row['Person 1']} × {row['Person 2']}: {row['Compatibility %']}%")

if __name__ == "__main__":
    from pathlib import Path
    import sys

    # Input dir: arg1 or current directory
    input_dir = Path(sys.argv[1]).expanduser().resolve() if len(sys.argv) > 1 else Path.cwd()

    # Output dir: "outputs" inside the input dir
    output_dir = input_dir / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    analyzer = ReadingCompatibilityAnalyzer()

    # Process all CSV files in the chosen directory
    results = analyzer.process_all_files(str(input_dir))

    if results:
        analyzer.save_results(str(output_dir / "compatibility_results.json"))
        analyzer.save_summary_csv(str(output_dir / "compatibility_summary.csv"))

        print("\n✅ Analysis complete!")
        print(f"Results: {output_dir / 'compatibility_results.json'}")
        print(f"Summary: {output_dir / 'compatibility_summary.csv'}")

