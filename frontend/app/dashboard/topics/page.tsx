'use client';

import { useState } from 'react';
import { DashboardLayout } from '@/components/dashboard-layout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api-client';
import { TrendingUp, Search, Loader2 } from 'lucide-react';

interface Topic {
  topic_name: string;
  relevance_score: number;
  citation_velocity: number;
  emerging_trend: boolean;
  related_keywords: string[];
}

export default function TopicsPage() {
  const [discipline, setDiscipline] = useState('');
  const [limit, setLimit] = useState('10');
  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFetchTopics = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const params: any = { limit: parseInt(limit) };
      if (discipline.trim()) {
        params.discipline = discipline.trim();
      }

      const response: any = await apiClient.getTrendingTopics(params);
      setTopics(response.topics || []);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch trending topics');
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Topic Discovery</h2>
          <p className="text-gray-600 mt-2">
            Discover trending research topics and emerging areas in your field
          </p>
        </div>

        {/* Search Form */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Search className="h-5 w-5" />
              Find Trending Topics
            </CardTitle>
            <CardDescription>
              Search for trending topics by discipline or browse all areas
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleFetchTopics} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="discipline">Discipline (Optional)</Label>
                  <Input
                    id="discipline"
                    type="text"
                    placeholder="e.g., Computer Science, Biology"
                    value={discipline}
                    onChange={(e) => setDiscipline(e.target.value)}
                    disabled={loading}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="limit">Number of Topics</Label>
                  <Input
                    id="limit"
                    type="number"
                    min="1"
                    max="50"
                    value={limit}
                    onChange={(e) => setLimit(e.target.value)}
                    disabled={loading}
                  />
                </div>
              </div>

              <Button type="submit" disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Fetching Topics...
                  </>
                ) : (
                  <>
                    <TrendingUp className="mr-2 h-4 w-4" />
                    Get Trending Topics
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Results */}
        {topics.length > 0 && (
          <div className="space-y-4">
            <h3 className="text-xl font-semibold text-gray-900">
              Found {topics.length} Trending Topics
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {topics.map((topic, index) => (
                <Card key={index} className="hover:shadow-md transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <CardTitle className="text-lg">{topic.topic_name}</CardTitle>
                      {topic.emerging_trend && (
                        <Badge variant="default" className="bg-green-600">
                          Emerging
                        </Badge>
                      )}
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Relevance Score</span>
                      <span className="font-semibold">
                        {(topic.relevance_score * 100).toFixed(1)}%
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Citation Velocity</span>
                      <span className="font-semibold flex items-center gap-1">
                        <TrendingUp className="h-4 w-4 text-blue-600" />
                        {topic.citation_velocity.toFixed(2)}
                      </span>
                    </div>

                    {topic.related_keywords && topic.related_keywords.length > 0 && (
                      <div className="space-y-2">
                        <span className="text-sm text-muted-foreground">Keywords</span>
                        <div className="flex flex-wrap gap-1">
                          {topic.related_keywords.map((keyword, idx) => (
                            <Badge key={idx} variant="outline" className="text-xs">
                              {keyword}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && topics.length === 0 && !error && (
          <Card className="text-center py-12">
            <CardContent>
              <TrendingUp className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                No Topics Yet
              </h3>
              <p className="text-gray-600 mb-4">
                Click the button above to discover trending research topics
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
