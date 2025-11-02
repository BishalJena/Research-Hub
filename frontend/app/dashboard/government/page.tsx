'use client';

import { useState } from 'react';
import { DashboardLayout } from '@/components/dashboard-layout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { apiClient } from '@/lib/api-client';
import { Building2, Loader2, Target, Award, DollarSign } from 'lucide-react';

interface GovernmentScheme {
  scheme_name: string;
  department: string;
  match_score: number;
  description: string;
  eligibility: string[];
}

interface FundingOpportunity {
  title: string;
  organization: string;
  amount: string;
  deadline: string;
  relevance: number;
}

interface SDGMapping {
  goal: string;
  relevance: number;
  target_areas: string[];
}

interface AlignmentResult {
  alignment_score: number;
  matched_schemes: GovernmentScheme[];
  funding_opportunities: FundingOpportunity[];
  sdg_mappings: SDGMapping[];
  priority_areas: string[];
}

export default function GovernmentPage() {
  const [researchTopic, setResearchTopic] = useState('');
  const [researchAbstract, setResearchAbstract] = useState('');
  const [keywords, setKeywords] = useState('');
  const [result, setResult] = useState<AlignmentResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!researchTopic.trim() || !researchAbstract.trim() || !keywords.trim()) {
      setError('Please fill in all fields');
      return;
    }

    setError('');
    setLoading(true);
    setResult(null);

    try {
      const keywordArray = keywords.split(',').map(k => k.trim()).filter(k => k);

      const response: any = await apiClient.analyzeGovernmentAlignment({
        research_topic: researchTopic.trim(),
        research_abstract: researchAbstract.trim(),
        keywords: keywordArray,
      });

      setResult({
        alignment_score: response.alignment_score || 0,
        matched_schemes: response.matched_schemes || [],
        funding_opportunities: response.funding_opportunities || [],
        sdg_mappings: response.sdg_mappings || [],
        priority_areas: response.priority_areas || [],
      });
    } catch (err: any) {
      setError(err.message || 'Failed to analyze government alignment');
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.7) return 'text-green-600';
    if (score >= 0.5) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Government Alignment</h2>
          <p className="text-gray-600 mt-2">
            Align your research with government priorities and funding opportunities
          </p>
        </div>

        {/* Input Form */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Building2 className="h-5 w-5" />
              Analyze Research Alignment
            </CardTitle>
            <CardDescription>
              Enter your research details to check alignment with government priorities and SDGs
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleAnalyze} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="topic">Research Topic</Label>
                <Input
                  id="topic"
                  type="text"
                  placeholder="e.g., Agricultural Technology for Farmers"
                  value={researchTopic}
                  onChange={(e) => setResearchTopic(e.target.value)}
                  disabled={loading}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="abstract">Research Abstract</Label>
                <Textarea
                  id="abstract"
                  placeholder="Provide a brief abstract of your research..."
                  value={researchAbstract}
                  onChange={(e) => setResearchAbstract(e.target.value)}
                  disabled={loading}
                  className="min-h-[150px]"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="keywords">Keywords</Label>
                <Input
                  id="keywords"
                  type="text"
                  placeholder="agriculture, technology, sustainability (comma-separated)"
                  value={keywords}
                  onChange={(e) => setKeywords(e.target.value)}
                  disabled={loading}
                  required
                />
                <p className="text-sm text-muted-foreground">
                  Separate keywords with commas
                </p>
              </div>

              <Button type="submit" disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Analyzing Alignment...
                  </>
                ) : (
                  <>
                    <Target className="mr-2 h-4 w-4" />
                    Analyze Alignment
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
            {/* Alignment Score */}
            <Card>
              <CardHeader>
                <CardTitle>Overall Alignment Score</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-center">
                  <div className="text-center">
                    <div className={`text-6xl font-bold ${getScoreColor(result.alignment_score)}`}>
                      {(result.alignment_score * 100).toFixed(0)}%
                    </div>
                    <p className="text-muted-foreground mt-2">Government Alignment</p>
                  </div>
                </div>

                <Progress value={result.alignment_score * 100} />

                {result.priority_areas && result.priority_areas.length > 0 && (
                  <div className="space-y-2">
                    <p className="text-sm font-medium">Priority Areas</p>
                    <div className="flex flex-wrap gap-2">
                      {result.priority_areas.map((area, idx) => (
                        <Badge key={idx} variant="outline">
                          {area}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Matched Schemes */}
            {result.matched_schemes && result.matched_schemes.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Award className="h-5 w-5" />
                    Matched Government Schemes
                  </CardTitle>
                  <CardDescription>
                    {result.matched_schemes.length} relevant schemes found
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {result.matched_schemes.map((scheme, index) => (
                      <div key={index} className="border rounded-lg p-4 space-y-3">
                        <div className="flex items-start justify-between">
                          <div>
                            <h4 className="font-semibold">{scheme.scheme_name}</h4>
                            <p className="text-sm text-muted-foreground">{scheme.department}</p>
                          </div>
                          <Badge variant="outline">
                            {(scheme.match_score * 100).toFixed(0)}% match
                          </Badge>
                        </div>

                        <p className="text-sm text-gray-700">{scheme.description}</p>

                        {scheme.eligibility && scheme.eligibility.length > 0 && (
                          <div className="space-y-1">
                            <p className="text-sm font-medium">Eligibility:</p>
                            <ul className="list-disc list-inside space-y-1">
                              {scheme.eligibility.map((item, idx) => (
                                <li key={idx} className="text-sm text-gray-600">
                                  {item}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Funding Opportunities */}
            {result.funding_opportunities && result.funding_opportunities.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <DollarSign className="h-5 w-5" />
                    Funding Opportunities
                  </CardTitle>
                  <CardDescription>
                    {result.funding_opportunities.length} funding opportunities available
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {result.funding_opportunities.map((funding, index) => (
                      <div key={index} className="border rounded-lg p-4 space-y-2">
                        <div className="flex items-start justify-between">
                          <h4 className="font-semibold">{funding.title}</h4>
                          <Badge variant="default">
                            {(funding.relevance * 100).toFixed(0)}% relevant
                          </Badge>
                        </div>

                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <p className="text-muted-foreground">Organization</p>
                            <p className="font-medium">{funding.organization}</p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">Amount</p>
                            <p className="font-medium">{funding.amount}</p>
                          </div>
                        </div>

                        <div className="text-sm">
                          <p className="text-muted-foreground">Deadline</p>
                          <p className="font-medium">{funding.deadline}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* SDG Mappings */}
            {result.sdg_mappings && result.sdg_mappings.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>SDG Alignment</CardTitle>
                  <CardDescription>
                    Sustainable Development Goals related to your research
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {result.sdg_mappings.map((sdg, index) => (
                      <div key={index} className="border rounded-lg p-4 space-y-2">
                        <div className="flex items-center justify-between">
                          <h4 className="font-semibold">{sdg.goal}</h4>
                          <Badge variant="outline">
                            {(sdg.relevance * 100).toFixed(0)}% relevant
                          </Badge>
                        </div>

                        {sdg.target_areas && sdg.target_areas.length > 0 && (
                          <div className="flex flex-wrap gap-1">
                            {sdg.target_areas.map((area, idx) => (
                              <Badge key={idx} variant="secondary" className="text-xs">
                                {area}
                              </Badge>
                            ))}
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
              <Building2 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Ready to Analyze
              </h3>
              <p className="text-gray-600 mb-4">
                Enter your research details to check alignment with government priorities
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
