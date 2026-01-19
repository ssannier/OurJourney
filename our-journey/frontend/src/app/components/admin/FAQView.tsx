import { useState } from 'react';
import { TrendingUp, HelpCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';

// Mock FAQ data generated from conversation patterns
const mockFAQs = [
  {
    question: 'How can I find housing after release?',
    category: 'Housing',
    askedCount: 157,
    keywords: ['housing', 'shelter', 'transitional housing', 'place to stay'],
    suggestedAnswer: 'Resources include OurJourney Housing Support, NC Coalition for Supportive Housing'
  },
  {
    question: 'Where can I find employers who hire people with records?',
    category: 'Jobs',
    askedCount: 142,
    keywords: ['job', 'work', 'employment', 'second chance employer', 'hire felons'],
    suggestedAnswer: 'Check out OurJourney Job Board, NC Works Career Center, and Second Chance Alliance'
  },
  {
    question: 'How do I get my ID or driver\'s license?',
    category: 'ID/Documents',
    askedCount: 128,
    keywords: ['id', 'identification', 'drivers license', 'dmv', 'state id'],
    suggestedAnswer: 'Visit NC DMV for ID/license services. Bring required documents.'
  },
  {
    question: 'What healthcare options are available?',
    category: 'Healthcare',
    askedCount: 98,
    keywords: ['healthcare', 'doctor', 'medical', 'insurance', 'medicaid'],
    suggestedAnswer: 'Alliance Health provides mental health and substance use services. Apply for Medicaid at NC DHHS.'
  },
  {
    question: 'How can I get legal help for my record?',
    category: 'Legal',
    askedCount: 87,
    keywords: ['legal', 'lawyer', 'expungement', 'record', 'attorney'],
    suggestedAnswer: 'Legal Aid of North Carolina offers free legal assistance for low-income individuals.'
  },
  {
    question: 'What transportation options do I have?',
    category: 'Transportation',
    askedCount: 76,
    keywords: ['transportation', 'bus', 'ride', 'get around', 'public transit'],
    suggestedAnswer: 'Public transit varies by county. Check GoTriangle, Charlotte CATS, or your county transit.'
  },
  {
    question: 'How do I apply for food stamps or benefits?',
    category: 'Benefits',
    askedCount: 65,
    keywords: ['food stamps', 'snap', 'benefits', 'assistance', 'ebt'],
    suggestedAnswer: 'Apply online at NC DHHS Benefits Portal or call 1-800-662-7030'
  },
  {
    question: 'What resources are available for addiction/mental health?',
    category: 'Health',
    askedCount: 54,
    keywords: ['addiction', 'mental health', 'counseling', 'therapy', 'substance abuse'],
    suggestedAnswer: 'Alliance Health: 1-800-510-9132. Also check local county health departments.'
  },
  {
    question: 'How can I reconnect with my family?',
    category: 'Family',
    askedCount: 43,
    keywords: ['family', 'kids', 'children', 'visitation', 'custody'],
    suggestedAnswer: 'Family support services vary by county. Contact local DSS for family reunification resources.'
  },
  {
    question: 'What do I need to know about my probation/parole?',
    category: 'Probation',
    askedCount: 39,
    keywords: ['probation', 'parole', 'officer', 'check in', 'supervision'],
    suggestedAnswer: 'Follow all terms of your supervision. Contact your PO immediately if you have questions.'
  }
];

export const FAQView = () => {
  const [sortBy, setSortBy] = useState<'frequency' | 'category'>('frequency');

  const sortedFAQs = [...mockFAQs].sort((a, b) => {
    if (sortBy === 'frequency') {
      return b.askedCount - a.askedCount;
    }
    return a.category.localeCompare(b.category);
  });

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">Frequently Asked Questions</h2>
          <p className="text-gray-600">Common questions identified from user conversations</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setSortBy('frequency')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              sortBy === 'frequency'
                ? 'bg-[#1B5E20] text-white'
                : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
            }`}
          >
            By Frequency
          </button>
          <button
            onClick={() => setSortBy('category')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              sortBy === 'category'
                ? 'bg-[#1B5E20] text-white'
                : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
            }`}
          >
            By Category
          </button>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-[#E8F5E9] rounded-full flex items-center justify-center">
                <HelpCircle className="w-6 h-6 text-[#1B5E20]" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{mockFAQs.length}</p>
                <p className="text-sm text-gray-600">Common Questions</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-[#E8F5E9] rounded-full flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-[#1B5E20]" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">
                  {mockFAQs.reduce((sum, faq) => sum + faq.askedCount, 0)}
                </p>
                <p className="text-sm text-gray-600">Total Questions Asked</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-[#E8F5E9] rounded-full flex items-center justify-center">
                <span className="text-xl">📊</span>
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{mockFAQs[0].category}</p>
                <p className="text-sm text-gray-600">Top Category</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* FAQs List */}
      <div className="space-y-3">
        {sortedFAQs.map((faq, idx) => (
          <Card key={idx} className="hover:shadow-md transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <Badge className="bg-[#E8F5E9] text-[#1B5E20]">{faq.category}</Badge>
                    <Badge variant="outline">Asked {faq.askedCount} times</Badge>
                  </div>
                  <CardTitle className="text-lg">{faq.question}</CardTitle>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-[#388E3C]">#{idx + 1}</div>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-1">Suggested Answer:</p>
                  <p className="text-sm text-gray-600">{faq.suggestedAnswer}</p>
                </div>
                
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-1">Common Keywords:</p>
                  <div className="flex flex-wrap gap-2">
                    {faq.keywords.map((keyword, kidx) => (
                      <span
                        key={kidx}
                        className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded"
                      >
                        {keyword}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="pt-3 border-t border-gray-200">
                  <button className="text-sm text-[#388E3C] hover:text-[#1B5E20] font-medium">
                    + Add to Knowledge Base
                  </button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};
