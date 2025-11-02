'use client';

import { useAuth } from '@/lib/auth-context';
import { DashboardLayout } from '@/components/dashboard-layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, FileText, Shield, BookOpen, Building2, BarChart3 } from 'lucide-react';
import Link from 'next/link';

const features = [
  {
    title: 'Topic Discovery',
    description: 'Discover trending research topics and track their evolution',
    icon: TrendingUp,
    href: '/dashboard/topics',
    color: 'text-blue-600',
    bgColor: 'bg-blue-50',
  },
  {
    title: 'Paper Analysis',
    description: 'Upload and analyze research papers with AI-powered insights',
    icon: FileText,
    href: '/dashboard/papers',
    color: 'text-green-600',
    bgColor: 'bg-green-50',
  },
  {
    title: 'Plagiarism Check',
    description: 'Ensure originality with advanced plagiarism detection',
    icon: Shield,
    href: '/dashboard/plagiarism',
    color: 'text-red-600',
    bgColor: 'bg-red-50',
  },
  {
    title: 'Journal Finder',
    description: 'Get personalized journal recommendations for your research',
    icon: BookOpen,
    href: '/dashboard/journals',
    color: 'text-purple-600',
    bgColor: 'bg-purple-50',
  },
  {
    title: 'Government Alignment',
    description: 'Align research with government priorities and SDG goals',
    icon: Building2,
    href: '/dashboard/government',
    color: 'text-orange-600',
    bgColor: 'bg-orange-50',
  },
  {
    title: 'Impact Prediction',
    description: 'Predict the real-world impact of your research',
    icon: BarChart3,
    href: '/dashboard/impact',
    color: 'text-indigo-600',
    bgColor: 'bg-indigo-50',
  },
];

export default function DashboardPage() {
  const { user } = useAuth();

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Welcome Section */}
        <div>
          <h2 className="text-3xl font-bold text-gray-900">
            Welcome back, {user?.full_name?.split(' ')[0] || 'Researcher'}!
          </h2>
          <p className="text-gray-600 mt-2">
            Explore AI-powered tools to accelerate your research journey
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardHeader className="pb-3">
              <CardDescription>Active Projects</CardDescription>
              <CardTitle className="text-3xl">0</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Start by uploading a research paper
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardDescription>Papers Analyzed</CardDescription>
              <CardTitle className="text-3xl">0</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Use our AI-powered analysis tools
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardDescription>Plagiarism Checks</CardDescription>
              <CardTitle className="text-3xl">0</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Ensure originality of your work
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Features Grid */}
        <div>
          <h3 className="text-xl font-semibold text-gray-900 mb-4">
            Research Tools
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature) => {
              const Icon = feature.icon;
              return (
                <Link key={feature.href} href={feature.href}>
                  <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
                    <CardHeader>
                      <div className={`w-12 h-12 rounded-lg ${feature.bgColor} flex items-center justify-center mb-3`}>
                        <Icon className={`h-6 w-6 ${feature.color}`} />
                      </div>
                      <CardTitle className="text-lg">{feature.title}</CardTitle>
                      <CardDescription>{feature.description}</CardDescription>
                    </CardHeader>
                  </Card>
                </Link>
              );
            })}
          </div>
        </div>

        {/* Quick Start Guide */}
        <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
          <CardHeader>
            <CardTitle>Getting Started</CardTitle>
            <CardDescription>
              Follow these steps to make the most of Smart Research Hub
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center text-sm font-bold flex-shrink-0">
                1
              </div>
              <div>
                <p className="font-medium">Upload your research paper</p>
                <p className="text-sm text-muted-foreground">
                  Start by uploading a paper for AI-powered analysis
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center text-sm font-bold flex-shrink-0">
                2
              </div>
              <div>
                <p className="font-medium">Check for plagiarism</p>
                <p className="text-sm text-muted-foreground">
                  Ensure originality before submission
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center text-sm font-bold flex-shrink-0">
                3
              </div>
              <div>
                <p className="font-medium">Find the perfect journal</p>
                <p className="text-sm text-muted-foreground">
                  Get personalized journal recommendations
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center text-sm font-bold flex-shrink-0">
                4
              </div>
              <div>
                <p className="font-medium">Predict research impact</p>
                <p className="text-sm text-muted-foreground">
                  Understand the potential impact of your work
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
