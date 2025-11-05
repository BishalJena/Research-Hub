'use client';

import { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/dashboard-layout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api-client';
import { BarChart3, Loader2, Users, DollarSign, Calendar, MapPin } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface District {
  id: number;
  name: string;
  population: number;
}

interface DistrictImpact {
  district: string;
  population_reach: number;
  economic_benefit: number;
  social_score: number;
}

interface ImpactResult {
  overall_impact_score: number;
  population_reach: number;
  economic_benefits: string;
  timeline: string;
  district_impacts: DistrictImpact[];
  key_metrics: {
    jobs_created: number;
    beneficiaries: number;
    roi_percentage: number;
  };
}

export default function ImpactPage() {
  const [researchTopic, setResearchTopic] = useState('');
  const [researchAbstract, setResearchAbstract] = useState('');
  const [districts, setDistricts] = useState<District[]>([]);
  const [selectedDistricts, setSelectedDistricts] = useState<string[]>([]);
  const [result, setResult] = useState<ImpactResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingDistricts, setLoadingDistricts] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDistricts();
  }, []);

  const fetchDistricts = async () => {
    setLoadingDistricts(true);
    try {
      const response: any = await apiClient.getDistricts();
      setDistricts(response.districts || []);
    } catch (err: any) {
      console.error('Failed to load districts:', err);
    } finally {
      setLoadingDistricts(false);
    }
  };

  const handleDistrictToggle = (districtName: string) => {
    setSelectedDistricts(prev => {
      if (prev.includes(districtName)) {
        return prev.filter(d => d !== districtName);
      } else {
        return [...prev, districtName];
      }
    });
  };

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!researchTopic.trim() || !researchAbstract.trim()) {
      setError('Please fill in all required fields');
      return;
    }

    setError('');
    setLoading(true);
    setResult(null);

    try {
      const response: any = await apiClient.predictImpact({
        research_topic: researchTopic.trim(),
        research_abstract: researchAbstract.trim(),
        target_districts: selectedDistricts.length > 0 ? selectedDistricts : undefined,
      });

      setResult({
        overall_impact_score: response.overall_impact_score || 0,
        population_reach: response.population_reach || 0,
        economic_benefits: response.economic_benefits || 'Not available',
        timeline: response.timeline || 'Not specified',
        district_impacts: response.district_impacts || [],
        key_metrics: response.key_metrics || {
          jobs_created: 0,
          beneficiaries: 0,
          roi_percentage: 0,
        },
      });
    } catch (err: any) {
      setError(err.message || 'Failed to predict impact');
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Impact Prediction</h2>
          <p className="text-gray-600 mt-2">
            Predict the real-world impact of your research across Andhra Pradesh
          </p>
        </div>

        {/* Input Form */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Analyze Research Impact
            </CardTitle>
            <CardDescription>
              Enter your research details to predict population reach and economic benefits
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handlePredict} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="topic">Research Topic</Label>
                <Input
                  id="topic"
                  type="text"
                  placeholder="e.g., Smart Irrigation System for Small Farmers"
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
                  placeholder="Describe your research and its potential applications..."
                  value={researchAbstract}
                  onChange={(e) => setResearchAbstract(e.target.value)}
                  disabled={loading}
                  className="min-h-[150px]"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label>Target Districts (Optional)</Label>
                {loadingDistricts ? (
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Loading districts...
                  </div>
                ) : (
                  <div className="border rounded-md p-4 max-h-48 overflow-y-auto">
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                      {districts.map((district) => (
                        <label
                          key={district.name}
                          className="flex items-center gap-2 cursor-pointer"
                        >
                          <input
                            type="checkbox"
                            checked={selectedDistricts.includes(district.name)}
                            onChange={() => handleDistrictToggle(district.name)}
                            disabled={loading}
                            className="rounded"
                          />
                          <span className="text-sm">{district.name}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                )}
                <p className="text-sm text-muted-foreground">
                  Select specific districts to focus the impact analysis
                </p>
              </div>

              <Button type="submit" disabled={loading}>
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Predicting Impact...
                  </>
                ) : (
                  <>
                    <BarChart3 className="mr-2 h-4 w-4" />
                    Predict Impact
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
            {/* Overall Score */}
            <Card>
              <CardHeader>
                <CardTitle>Overall Impact Score</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-6xl font-bold text-blue-600">
                      {(result.overall_impact_score * 100).toFixed(0)}
                    </div>
                    <p className="text-muted-foreground mt-2">Impact Score</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card>
                <CardHeader className="pb-3">
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Users className="h-4 w-4" />
                    <CardDescription>Population Reach</CardDescription>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold text-gray-900">
                    {formatNumber(result.population_reach)}
                  </p>
                  <p className="text-sm text-muted-foreground mt-1">
                    People impacted
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <DollarSign className="h-4 w-4" />
                    <CardDescription>Economic Benefits</CardDescription>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold text-gray-900">
                    {result.economic_benefits}
                  </p>
                  <p className="text-sm text-muted-foreground mt-1">
                    Estimated value
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-3">
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Calendar className="h-4 w-4" />
                    <CardDescription>Timeline</CardDescription>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold text-gray-900">
                    {result.timeline}
                  </p>
                  <p className="text-sm text-muted-foreground mt-1">
                    Expected duration
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Key Metrics Detail */}
            {result.key_metrics && (
              <Card>
                <CardHeader>
                  <CardTitle>Key Impact Metrics</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="space-y-2">
                      <p className="text-sm text-muted-foreground">Jobs Created</p>
                      <p className="text-2xl font-bold text-gray-900">
                        {formatNumber(result.key_metrics.jobs_created)}
                      </p>
                    </div>

                    <div className="space-y-2">
                      <p className="text-sm text-muted-foreground">Direct Beneficiaries</p>
                      <p className="text-2xl font-bold text-gray-900">
                        {formatNumber(result.key_metrics.beneficiaries)}
                      </p>
                    </div>

                    <div className="space-y-2">
                      <p className="text-sm text-muted-foreground">Expected ROI</p>
                      <p className="text-2xl font-bold text-gray-900">
                        {result.key_metrics.roi_percentage.toFixed(1)}%
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* District-wise Impact */}
            {result.district_impacts && result.district_impacts.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <MapPin className="h-5 w-5" />
                    District-wise Impact Analysis
                  </CardTitle>
                  <CardDescription>
                    Impact breakdown across {result.district_impacts.length} districts
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {result.district_impacts.map((impact) => (
                      <div key={impact.district} className="border rounded-lg p-4">
                        <h4 className="font-semibold mb-3">{impact.district}</h4>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          <div className="space-y-1">
                            <p className="text-sm text-muted-foreground">Population Reach</p>
                            <p className="text-lg font-bold text-gray-900">
                              {formatNumber(impact.population_reach)}
                            </p>
                          </div>

                          <div className="space-y-1">
                            <p className="text-sm text-muted-foreground">Economic Benefit</p>
                            <p className="text-lg font-bold text-gray-900">
                              ₹{formatNumber(impact.economic_benefit)}
                            </p>
                          </div>

                          <div className="space-y-1">
                            <p className="text-sm text-muted-foreground">Social Impact Score</p>
                            <div className="flex items-center gap-2">
                              <p className="text-lg font-bold text-gray-900">
                                {(impact.social_score * 100).toFixed(0)}%
                              </p>
                              <Badge variant="outline">
                                {impact.social_score >= 0.7 ? 'High' : impact.social_score >= 0.5 ? 'Medium' : 'Low'}
                              </Badge>
                            </div>
                          </div>
                        </div>
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
              <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Ready to Predict
              </h3>
              <p className="text-gray-600 mb-4">
                Enter your research details to predict its real-world impact
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
