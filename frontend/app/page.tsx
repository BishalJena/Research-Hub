'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Sparkles, FileText, CheckCircle, BookOpen, TrendingUp, Globe } from 'lucide-react';

export default function Home() {
  const { isAuthenticated, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, loading, router]);

  // Show loading state while checking authentication
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  // Don't redirect if already authenticated, just show loading
  if (isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Redirecting to dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="h-8 w-8 text-primary" />
            <span className="text-2xl font-bold">Smart Research Hub</span>
          </div>
          <div className="flex gap-2">
            <Button variant="ghost" onClick={() => router.push('/login')}>
              Login
            </Button>
            <Button onClick={() => router.push('/register')}>
              Get Started
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <h1 className="text-5xl font-bold tracking-tight mb-6">
          AI-Powered Research Platform
          <br />
          <span className="text-primary">for Andhra Pradesh</span>
        </h1>
        <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
          Discover trends, analyze papers, check plagiarism, and align your research with
          AP Government priorities - all in one intelligent platform.
        </p>
        <div className="flex gap-4 justify-center">
          <Button size="lg" onClick={() => router.push('/register')}>
            Start Free Today
          </Button>
          <Button size="lg" variant="outline" onClick={() => router.push('/login')}>
            Sign In
          </Button>
        </div>
      </section>

      {/* Features */}
      <section className="container mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center mb-12">Everything You Need for Research Excellence</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card>
            <CardHeader>
              <TrendingUp className="h-10 w-10 text-primary mb-2" />
              <CardTitle>Topic Discovery</CardTitle>
              <CardDescription>
                Find trending research topics in your field using AI-powered analysis
              </CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <FileText className="h-10 w-10 text-primary mb-2" />
              <CardTitle>Paper Analysis</CardTitle>
              <CardDescription>
                Auto-summarize research papers with AI and find related work instantly
              </CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <CheckCircle className="h-10 w-10 text-primary mb-2" />
              <CardTitle>Plagiarism Detection</CardTitle>
              <CardDescription>
                Multi-layer similarity detection with semantic analysis
              </CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <BookOpen className="h-10 w-10 text-primary mb-2" />
              <CardTitle>Journal Recommendations</CardTitle>
              <CardDescription>
                Get personalized journal recommendations based on your research
              </CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <Globe className="h-10 w-10 text-primary mb-2" />
              <CardTitle>Government Alignment</CardTitle>
              <CardDescription>
                Map research to AP Government priorities and funding opportunities
              </CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <Sparkles className="h-10 w-10 text-primary mb-2" />
              <CardTitle>Impact Prediction</CardTitle>
              <CardDescription>
                Quantify real-world impact with district-level demographic data
              </CardDescription>
            </CardHeader>
          </Card>
        </div>
      </section>

      {/* Stats */}
      <section className="container mx-auto px-4 py-16 text-center">
        <div className="grid md:grid-cols-4 gap-8">
          <div>
            <div className="text-4xl font-bold text-primary">6</div>
            <div className="text-muted-foreground">AI Modules</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-primary">5</div>
            <div className="text-muted-foreground">Languages Supported</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-primary">₹33,200 Cr</div>
            <div className="text-muted-foreground">Gov Schemes Tracked</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-primary">13</div>
            <div className="text-muted-foreground">AP Districts</div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="container mx-auto px-4 py-16">
        <Card className="bg-primary text-primary-foreground">
          <CardHeader className="text-center">
            <CardTitle className="text-3xl">Ready to Transform Your Research?</CardTitle>
            <CardDescription className="text-primary-foreground/80 text-lg">
              Join researchers from across Andhra Pradesh
            </CardDescription>
          </CardHeader>
          <CardContent className="flex justify-center">
            <Button
              size="lg"
              variant="secondary"
              onClick={() => router.push('/register')}
            >
              Create Free Account
            </Button>
          </CardContent>
        </Card>
      </section>

      {/* Footer */}
      <footer className="border-t mt-16">
        <div className="container mx-auto px-4 py-8 text-center text-muted-foreground">
          <p>© 2024 Smart Research Hub. Built for AP Government Colleges.</p>
        </div>
      </footer>
    </div>
  );
}
