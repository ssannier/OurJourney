import { MessageSquare, Users, AlertCircle, TrendingUp, Calendar } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';

// Mock data - in a real app, this would come from an API/database
const mockStats = {
  totalConversations: {
    today: 45,
    week: 312,
    month: 1247
  },
  activeUsers: {
    today: 38,
    week: 267,
    month: 1089
  },
  flaggedConversations: {
    crisis: 3,
    followup: 12,
    total: 15
  },
  topCategories: [
    { name: 'Housing', count: 423 },
    { name: 'Jobs & Training', count: 387 },
    { name: 'ID & Documents', count: 298 },
    { name: 'Healthcare', count: 245 },
    { name: 'Legal Help', count: 189 }
  ]
};

export const AdminOverview = () => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-gray-900 mb-2">Dashboard Overview</h2>
        <p className="text-gray-600">Monitor JoJo chatbot activity and user engagement</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Conversations */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Conversations Today
            </CardTitle>
            <MessageSquare className="w-4 h-4 text-[#388E3C]" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">{mockStats.totalConversations.today}</div>
            <p className="text-xs text-gray-500 mt-1">
              {mockStats.totalConversations.week} this week
            </p>
          </CardContent>
        </Card>

        {/* Active Users */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Active Users
            </CardTitle>
            <Users className="w-4 h-4 text-[#388E3C]" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">{mockStats.activeUsers.today}</div>
            <p className="text-xs text-gray-500 mt-1">
              {mockStats.activeUsers.week} this week
            </p>
          </CardContent>
        </Card>

        {/* Flagged Items */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Flagged Items
            </CardTitle>
            <AlertCircle className="w-4 h-4 text-amber-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">{mockStats.flaggedConversations.total}</div>
            <p className="text-xs text-gray-500 mt-1">
              {mockStats.flaggedConversations.crisis} crisis, {mockStats.flaggedConversations.followup} follow-up
            </p>
          </CardContent>
        </Card>

        {/* Monthly Total */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              Monthly Total
            </CardTitle>
            <Calendar className="w-4 h-4 text-[#388E3C]" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">{mockStats.totalConversations.month}</div>
            <p className="text-xs text-gray-500 mt-1">
              {mockStats.activeUsers.month} unique users
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Top Categories */}
      <Card>
        <CardHeader>
          <CardTitle>Top Resource Categories</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {mockStats.topCategories.map((category, idx) => (
              <div key={category.name} className="flex items-center gap-4">
                <div className="w-8 text-sm text-gray-500">{idx + 1}.</div>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-gray-900">{category.name}</span>
                    <span className="text-sm text-gray-600">{category.count} requests</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-[#388E3C] h-2 rounded-full transition-all"
                      style={{ width: `${(category.count / mockStats.topCategories[0].count) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Recent Activity Placeholder */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[
              { time: '5 min ago', user: 'User #1247', action: 'Requested housing resources', county: 'Wake' },
              { time: '12 min ago', user: 'User #1246', action: 'Accessed job training info', county: 'Durham' },
              { time: '18 min ago', user: 'User #1245', action: 'Crisis support initiated', county: 'Mecklenburg', flag: true },
              { time: '25 min ago', user: 'User #1244', action: 'Searched for ID/documents', county: 'Guilford' },
              { time: '31 min ago', user: 'User #1243', action: 'Requested follow-up contact', county: 'Forsyth', flag: true }
            ].map((activity, idx) => (
              <div key={idx} className="flex items-center gap-4 pb-4 border-b border-gray-100 last:border-0 last:pb-0">
                <div className="w-16 text-xs text-gray-500">{activity.time}</div>
                <div className="flex-1">
                  <p className="text-sm text-gray-900">{activity.action}</p>
                  <p className="text-xs text-gray-500">{activity.user} • {activity.county} County</p>
                </div>
                {activity.flag && (
                  <AlertCircle className="w-4 h-4 text-amber-500" />
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
