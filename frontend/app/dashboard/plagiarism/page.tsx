'use client';

import { useState } from 'react';
import { DashboardLayout } from '@/components/dashboard-layout';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { apiClient } from '@/lib/api-client';
import { Shield, Loader2, AlertTriangle, CheckCircle } from 'lucide-react';

interface SimilarSource {
  source: string;
  similarity: number;
  matched_text: string;
}

interface PlagiarismResult {
  originality_score: number;
  plagiarism_detected: boolean;
  similar_sources: SimilarSource[];
  confidence: number;
  language: string;
}

export default function PlagiarismPage() {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<PlagiarismResult | null>(null);

  const handleCheck = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!text.trim()) {
      setError('Please enter text to check');
      return;
    }

    setError('');
    setLoading(true);
    setResult(null);

    try {
      const response: any = await apiClient.checkPlagiarism({
        text: text.trim(),
        check_online: true,
      });

      setResult({
        originality_score: response.originality_score || 0,
        plagiarism_detected: response.plagiarism_detected || false,
        similar_sources: response.similar_sources || [],
        confidence: response.confidence || 0,
        language: response.language || 'en',
      });
    } catch (err: any) {
      setError(err.message || 'Failed to check plagiarism');
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return 'bg-green-600';
    if (score >= 60) return 'bg-yellow-600';
    return 'bg-red-600';
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Plagiarism Check</h2>
          <p className="text-gray-600 mt-2">
            Ensure originality with advanced AI-powered plagiarism detection
          </p>
        </div>

        {/* Input Form */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              Check Your Text
            </CardTitle>
            <CardDescription>
              Paste your text below to check for plagiarism and get an originality score
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCheck} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="text">Text to Check</Label>
                <Textarea
                  id="text"
                  placeholder="Paste your research text here..."
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  disabled={loading}
                  className="min-h-[200px]"
                />
                <p className="text-sm text-muted-foreground">
                  {text.length} characters
                </p>
              </div>

              <Button type="submit" disabled={loading || !text.trim()}>
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Checking for Plagiarism...
                  </>
                ) : (
                  <>
                    <Shield className="mr-2 h-4 w-4" />
                    Check Plagiarism
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
        {result && (
          <div className="space-y-6">
            {/* Originality Score */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {result.plagiarism_detected ? (
                    <AlertTriangle className="h-5 w-5 text-yellow-600" />
                  ) : (
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  )}
                  Originality Score
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-center">
                  <div className="text-center">
                    <div className={`text-6xl font-bold ${getScoreColor(result.originality_score)}`}>
                      {result.originality_score.toFixed(1)}%
                    </div>
                    <p className="text-muted-foreground mt-2">Originality</p>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span>Score</span>
                    <span className="font-medium">{result.originality_score.toFixed(1)}%</span>
                  </div>
                  <Progress
                    value={result.originality_score}
                    className={getScoreBgColor(result.originality_score)}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Confidence</span>
                  <Badge variant="outline">
                    {(result.confidence * 100).toFixed(0)}% confident
                  </Badge>
                </div>

                {result.plagiarism_detected ? (
                  <Alert variant="destructive">
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>
                      Potential plagiarism detected. Review similar sources below.
                    </AlertDescription>
                  </Alert>
                ) : (
                  <Alert className="border-green-200 bg-green-50">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <AlertDescription className="text-green-800">
                      No significant plagiarism detected. Your content appears original.
                    </AlertDescription>
                  </Alert>
                )}
              </CardContent>
            </Card>

            {/* Similar Sources */}
            {result.similar_sources && result.similar_sources.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Similar Sources Found</CardTitle>
                  <CardDescription>
                    {result.similar_sources.length} potential matches detected
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {result.similar_sources.map((source, index) => (
                      <div
                        key={index}
                        className="border rounded-lg p-4 space-y-3"
                      >
                        <div className="flex items-center justify-between">
                          <h4 className="font-semibold text-sm">Source {index + 1}</h4>
                          <Badge
                            variant={source.similarity > 0.7 ? 'destructive' : 'outline'}
                          >
                            {(source.similarity * 100).toFixed(1)}% similar
                          </Badge>
                        </div>

                        <div className="space-y-2">
                          <p className="text-sm text-muted-foreground">Source:</p>
                          <p className="text-sm font-medium">{source.source}</p>
                        </div>

                        {source.matched_text && (
                          <div className="space-y-2">
                            <p className="text-sm text-muted-foreground">Matched Text:</p>
                            <div className="bg-yellow-50 border border-yellow-200 rounded p-3">
                              <p className="text-sm text-gray-700 italic">
                                "{source.matched_text}"
                              </p>
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}

        {/* Empty State */}
        {!loading && !result && !error && (
          <Card className="text-center py-12">
            <CardContent>
              <Shield className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Ready to Check
              </h3>
              <p className="text-gray-600 mb-4">
                Paste your text above and click "Check Plagiarism" to get started
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
