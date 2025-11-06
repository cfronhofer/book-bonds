"use client";

import { useState, useMemo } from "react";
import compatibilityData from "../stats/compatibility_results.json";
import type { CompatibilityData, CompatibilityResult } from "./types";

const data = compatibilityData as CompatibilityData;

export default function Home() {
  const [person1, setPerson1] = useState<string>("");
  const [person2, setPerson2] = useState<string>("");

  // Extract unique person names from the data
  const allPeople = useMemo(() => {
    const peopleSet = new Set<string>();
    data.results.forEach((result) => {
      peopleSet.add(result.person1);
      peopleSet.add(result.person2);
    });
    return Array.from(peopleSet).sort();
  }, []);

  // Find compatibility result for selected pair
  const compatibility = useMemo<CompatibilityResult | null>(() => {
    if (!person1 || !person2 || person1 === person2) return null;

    const result = data.results.find(
      (r) =>
        (r.person1 === person1 && r.person2 === person2) ||
        (r.person1 === person2 && r.person2 === person1)
    );

    return result || null;
  }, [person1, person2]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 dark:from-gray-900 dark:to-gray-800 py-12 px-4">
      <main className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-3">
            Book Bonds
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300">
            Discover your reading compatibility!
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 mb-8">
          <div className="grid md:grid-cols-2 gap-6 mb-8">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                First Person
              </label>
              <select
                value={person1}
                onChange={(e) => setPerson1(e.target.value)}
                className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition"
              >
                <option value="">Select a person...</option>
                {allPeople.map((person) => (
                  <option key={person} value={person} disabled={person === person2}>
                    {person}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Second Person
              </label>
              <select
                value={person2}
                onChange={(e) => setPerson2(e.target.value)}
                className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent transition"
              >
                <option value="">Select a person...</option>
                {allPeople.map((person) => (
                  <option key={person} value={person} disabled={person === person1}>
                    {person}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {compatibility && (
            <div className="space-y-6">
              {/* Compatibility Score */}
              <div className="text-center py-8 bg-gradient-to-r from-purple-100 to-blue-100 dark:from-purple-900/30 dark:to-blue-900/30 rounded-xl">
                <div className="text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-blue-600 mb-2">
                  {compatibility.compatibility_score}%
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Compatibility Score
                </p>
              </div>

              {/* Diagnosis */}
              <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                  Analysis
                </h3>
                <p className="text-gray-700 dark:text-gray-300">
                  {compatibility.diagnosis}
                </p>
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 rounded-lg p-4">
                  <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                    {compatibility.metrics.shared_books_finished}
                  </div>
                  <div className="text-xs text-gray-600 dark:text-gray-400">
                    Shared Books
                  </div>
                </div>
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-lg p-4">
                  <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                    {compatibility.metrics.shared_authors}
                  </div>
                  <div className="text-xs text-gray-600 dark:text-gray-400">
                    Shared Authors
                  </div>
                </div>
                <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-lg p-4">
                  <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                    {compatibility.metrics.cross_recommendations}
                  </div>
                  <div className="text-xs text-gray-600 dark:text-gray-400">
                    Cross Recommendations
                  </div>
                </div>
                <div className="bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20 rounded-lg p-4">
                  <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
                    {compatibility.metrics.shared_tbr}
                  </div>
                  <div className="text-xs text-gray-600 dark:text-gray-400">
                    Shared TBR
                  </div>
                </div>
              </div>

              {/* Shared Books */}
              {compatibility.top_shared_books.length > 0 && (
                <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-3">
                    Top Shared Books
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {compatibility.top_shared_books.map((book, idx) => (
                      <span
                        key={idx}
                        className="px-3 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 rounded-full text-sm capitalize"
                      >
                        {book}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Shared Authors */}
              {compatibility.top_shared_authors.length > 0 && (
                <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-3">
                    Top Shared Authors
                  </h3>
                  <div className="space-y-2">
                    {compatibility.top_shared_authors.slice(0, 5).map((author, idx) => (
                      <div
                        key={idx}
                        className="flex justify-between items-center p-2 bg-white dark:bg-gray-700 rounded"
                      >
                        <span className="text-gray-900 dark:text-white font-medium">
                          {author.author}
                        </span>
                        <span className="text-sm text-gray-500 dark:text-gray-400">
                          {person1}: {author.person1_count} | {person2}: {author.person2_count}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Score Breakdown */}
              <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 dark:text-white mb-3">
                  Score Breakdown
                </h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Shared Finished Books:</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {(compatibility.score_breakdown.shared_finished * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Shared Authors:</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {(compatibility.score_breakdown.shared_authors * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Cross Recommendations:</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {(compatibility.score_breakdown.cross_recommendations * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Shared TBR:</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {(compatibility.score_breakdown.shared_tbr * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Reading Behavior:</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {(compatibility.score_breakdown.reading_behavior * 100).toFixed(1)}%
                    </span>
                  </div>
                  {compatibility.score_breakdown.disagreement_penalty !== 0 && (
                    <div className="flex justify-between">
                      <span className="text-gray-600 dark:text-gray-400">Disagreement Penalty:</span>
                      <span className="font-medium text-red-600 dark:text-red-400">
                        {(compatibility.score_breakdown.disagreement_penalty * 100).toFixed(1)}%
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {!compatibility && person1 && person2 && person1 !== person2 && (
            <div className="text-center py-8 text-gray-500 dark:text-gray-400">
              No compatibility data found for this pairing.
            </div>
          )}

          {(!person1 || !person2 || person1 === person2) && (
            <div className="text-center py-8 text-gray-500 dark:text-gray-400">
              Select two different people to view their reading compatibility.
            </div>
          )}
        </div>

        <div className="text-center text-sm text-gray-500 dark:text-gray-400">
          Total pairings analyzed: {data.metadata.total_pairings} | Average compatibility:{" "}
          {data.metadata.average_compatibility}%
        </div>
      </main>
    </div>
  );
}
