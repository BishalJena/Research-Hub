'use client';

import { useState, useEffect } from 'react';
import { DashboardLayout } from '@/components/dashboard-layout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api-client';
import { FileText, Upload, Loader2, Trash2, Eye } from 'lucide-react';
import { Input } from '@/components/ui/input';

interface Paper {
  id: number;
  title: string;
  filename: string;
  uploaded_at: string;
  processed: boolean;
  summary?: string;
  key_findings?: string[];
  methodology?: string;
  created_at: string;
}

export default function PapersPage() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [processingIds, setProcessingIds] = useState<Set<number>>(new Set());
  const [error, setError] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  useEffect(() => {
    fetchPapers();
  }, []);

  const fetchPapers = async () => {
    setLoading(true);
    try {
      const response: any = await apiClient.listPapers();
      setPapers(response.papers || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load papers');
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file to upload');
      return;
    }

    setUploading(true);
    setError('');

    try {
      await apiClient.uploadPaper(selectedFile);
      setSelectedFile(null);
      // Reset file input
      const fileInput = document.getElementById('file-upload') as HTMLInputElement;
      if (fileInput) fileInput.value = '';

      await fetchPapers();
    } catch (err: any) {
      setError(err.message || 'Failed to upload paper');
    } finally {
      setUploading(false);
    }
  };

  const handleProcess = async (paperId: number) => {
    setProcessingIds(prev => new Set(prev).add(paperId));
    setError('');

    try {
      await apiClient.processPaper(paperId);
      await fetchPapers();
    } catch (err: any) {
      setError(err.message || 'Failed to process paper');
    } finally {
      setProcessingIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(paperId);
        return newSet;
      });
    }
  };

  const handleDelete = async (paperId: number) => {
    if (!confirm('Are you sure you want to delete this paper?')) {
      return;
    }

    try {
      await apiClient.deletePaper(paperId);
      await fetchPapers();
    } catch (err: any) {
      setError(err.message || 'Failed to delete paper');
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Paper Analysis</h2>
          <p className="text-gray-600 mt-2">
            Upload and analyze research papers with AI-powered insights
          </p>
        </div>

        {/* Upload Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Upload className="h-5 w-5" />
              Upload Research Paper
            </CardTitle>
            <CardDescription>
              Upload PDF files for AI-powered analysis and insights
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-end gap-4">
              <div className="flex-1">
                <Input
                  id="file-upload"
                  type="file"
                  accept=".pdf"
                  onChange={handleFileChange}
                  disabled={uploading}
                />
              </div>
              <Button onClick={handleUpload} disabled={uploading || !selectedFile}>
                {uploading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Uploading...
                  </>
                ) : (
                  <>
                    <Upload className="mr-2 h-4 w-4" />
                    Upload
                  </>
                )}
              </Button>
            </div>
            {selectedFile && (
              <p className="text-sm text-muted-foreground">
                Selected: {selectedFile.name}
              </p>
            )}
          </CardContent>
        </Card>

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Papers List */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
          </div>
        ) : papers.length > 0 ? (
          <div className="space-y-4">
            <h3 className="text-xl font-semibold text-gray-900">
              Your Papers ({papers.length})
            </h3>

            <div className="space-y-4">
              {papers.map((paper) => (
                <Card key={paper.id}>
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <CardTitle className="text-lg">{paper.title}</CardTitle>
                        <CardDescription className="mt-1">
                          {paper.filename} • Uploaded {new Date(paper.uploaded_at).toLocaleDateString()}
                        </CardDescription>
                      </div>
                      <div className="flex items-center gap-2">
                        {paper.processed ? (
                          <Badge variant="default" className="bg-green-600">
                            Processed
                          </Badge>
                        ) : (
                          <Badge variant="outline">Pending</Badge>
                        )}
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {paper.processed && paper.summary && (
                      <div className="space-y-2">
                        <h4 className="font-semibold text-sm">Summary</h4>
                        <p className="text-sm text-gray-700">{paper.summary}</p>
                      </div>
                    )}

                    {paper.processed && paper.methodology && (
                      <div className="space-y-2">
                        <h4 className="font-semibold text-sm">Methodology</h4>
                        <p className="text-sm text-gray-700">{paper.methodology}</p>
                      </div>
                    )}

                    {paper.processed && paper.key_findings && paper.key_findings.length > 0 && (
                      <div className="space-y-2">
                        <h4 className="font-semibold text-sm">Key Findings</h4>
                        <ul className="list-disc list-inside space-y-1">
                          {paper.key_findings.map((finding, idx) => (
                            <li key={idx} className="text-sm text-gray-700">
                              {finding}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    <div className="flex items-center gap-2 pt-2">
                      {!paper.processed && (
                        <Button
                          size="sm"
                          onClick={() => handleProcess(paper.id)}
                          disabled={processingIds.has(paper.id)}
                        >
                          {processingIds.has(paper.id) ? (
                            <>
                              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                              Processing...
                            </>
                          ) : (
                            <>
                              <Eye className="mr-2 h-4 w-4" />
                              Process Paper
                            </>
                          )}
                        </Button>
                      )}
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => handleDelete(paper.id)}
                      >
                        <Trash2 className="mr-2 h-4 w-4" />
                        Delete
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        ) : (
          <Card className="text-center py-12">
            <CardContent>
              <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                No Papers Yet
              </h3>
              <p className="text-gray-600 mb-4">
                Upload your first research paper to get started
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
