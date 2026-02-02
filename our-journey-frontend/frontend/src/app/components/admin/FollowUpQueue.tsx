import { useState } from 'react';
import { Phone, Mail, Clock, CircleCheck, User } from 'lucide-react';
import { Card, CardContent } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';

// Mock follow-up requests
const mockFollowUps = [
  {
    id: 'fu-1',
    userId: 'user-845',
    county: 'Mecklenburg',
    timestamp: '2025-12-28T14:14:00',
    requestType: 'crisis',
    email: 'user845@email.com',
    phone: '(704) 555-0123',
    preferredContact: 'phone',
    conversationSummary: 'User expressed feelings of hopelessness. Provided crisis resources. User requested follow-up.',
    status: 'new',
    priority: 'urgent',
    assignedTo: null
  },
  {
    id: 'fu-2',
    userId: 'user-843',
    county: 'Forsyth',
    timestamp: '2025-12-28T14:01:00',
    requestType: 'general',
    email: 'user843@email.com',
    phone: '',
    preferredContact: 'email',
    conversationSummary: 'User seeking housing and healthcare resources. Wants personalized assistance.',
    status: 'in-progress',
    priority: 'normal',
    assignedTo: 'Team Member A'
  },
  {
    id: 'fu-3',
    userId: 'user-840',
    county: 'Wake',
    timestamp: '2025-12-28T13:45:00',
    requestType: 'general',
    email: '',
    phone: '(919) 555-0156',
    preferredContact: 'phone',
    conversationSummary: 'User needs help navigating job training programs. Wants callback to discuss options.',
    status: 'new',
    priority: 'normal',
    assignedTo: null
  },
  {
    id: 'fu-4',
    userId: 'user-837',
    county: 'Durham',
    timestamp: '2025-12-28T12:30:00',
    requestType: 'general',
    email: 'user837@email.com',
    phone: '(919) 555-0187',
    preferredContact: 'email',
    conversationSummary: 'Questions about expungement process. Shared legal resources but user wants legal consultation.',
    status: 'completed',
    priority: 'normal',
    assignedTo: 'Team Member B'
  }
];

const statusColors = {
  'new': 'bg-blue-100 text-blue-700',
  'in-progress': 'bg-amber-100 text-amber-700',
  'completed': 'bg-green-100 text-green-700'
};

const priorityColors = {
  'urgent': 'bg-red-100 text-red-700',
  'normal': 'bg-gray-100 text-gray-700'
};

export const FollowUpQueue = () => {
  const [filterStatus, setFilterStatus] = useState('all');
  const [selectedItem, setSelectedItem] = useState<string | null>(null);

  const filteredItems = mockFollowUps.filter(item => {
    if (filterStatus === 'all') return true;
    return item.status === filterStatus;
  });

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    
    if (diffMins < 60) return `${diffMins} min ago`;
    if (diffHours < 24) return `${diffHours} hours ago`;
    return date.toLocaleDateString();
  };

  const handleStatusChange = (id: string, newStatus: string) => {
    console.log(`Changing status of ${id} to ${newStatus}`);
    // In real app, update via API
  };

  const handleAssign = (id: string, assignee: string) => {
    console.log(`Assigning ${id} to ${assignee}`);
    // In real app, update via API
  };

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">Follow-Up Queue</h2>
          <p className="text-gray-600">Users requesting personal follow-up from the OurJourney team</p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <p className="text-3xl font-bold text-blue-600">
                {mockFollowUps.filter(f => f.status === 'new').length}
              </p>
              <p className="text-sm text-gray-600 mt-1">New Requests</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <p className="text-3xl font-bold text-amber-600">
                {mockFollowUps.filter(f => f.status === 'in-progress').length}
              </p>
              <p className="text-sm text-gray-600 mt-1">In Progress</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <p className="text-3xl font-bold text-green-600">
                {mockFollowUps.filter(f => f.status === 'completed').length}
              </p>
              <p className="text-sm text-gray-600 mt-1">Completed</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <p className="text-3xl font-bold text-red-600">
                {mockFollowUps.filter(f => f.priority === 'urgent').length}
              </p>
              <p className="text-sm text-gray-600 mt-1">Urgent</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filter */}
      <div className="flex gap-4">
        <Select value={filterStatus} onValueChange={setFilterStatus}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Requests</SelectItem>
            <SelectItem value="new">New</SelectItem>
            <SelectItem value="in-progress">In Progress</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Follow-up Items */}
      <div className="space-y-3">
        {filteredItems.map((item) => (
          <Card 
            key={item.id}
            className={`transition-all hover:shadow-md ${
              selectedItem === item.id ? 'ring-2 ring-[#388E3C]' : ''
            } ${item.priority === 'urgent' ? 'border-l-4 border-l-red-500' : ''}`}
          >
            <CardContent className="p-4">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="font-semibold text-gray-900">{item.userId}</h3>
                    <Badge className={statusColors[item.status as keyof typeof statusColors]}>
                      {item.status.replace('-', ' ')}
                    </Badge>
                    {item.priority === 'urgent' && (
                      <Badge className={priorityColors.urgent}>
                        URGENT
                      </Badge>
                    )}
                    {item.requestType === 'crisis' && (
                      <Badge variant="destructive">
                        Crisis
                      </Badge>
                    )}
                  </div>
                  <p className="text-sm text-gray-600 mb-1">{item.county} County</p>
                  <p className="text-xs text-gray-500 flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    Requested {formatTime(item.timestamp)}
                  </p>
                </div>
              </div>

              {/* Contact Info */}
              <div className="bg-gray-50 rounded-lg p-3 mb-3">
                <p className="text-xs font-medium text-gray-600 mb-2">Contact Information:</p>
                <div className="space-y-1">
                  {item.email && (
                    <div className="flex items-center gap-2 text-sm">
                      <Mail className="w-4 h-4 text-gray-400" />
                      <a href={`mailto:${item.email}`} className="text-[#388E3C] hover:underline">
                        {item.email}
                      </a>
                      {item.preferredContact === 'email' && (
                        <Badge variant="outline" className="text-xs">Preferred</Badge>
                      )}
                    </div>
                  )}
                  {item.phone && (
                    <div className="flex items-center gap-2 text-sm">
                      <Phone className="w-4 h-4 text-gray-400" />
                      <a href={`tel:${item.phone}`} className="text-[#388E3C] hover:underline">
                        {item.phone}
                      </a>
                      {item.preferredContact === 'phone' && (
                        <Badge variant="outline" className="text-xs">Preferred</Badge>
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* Conversation Summary */}
              <div className="mb-3">
                <p className="text-xs font-medium text-gray-600 mb-1">Conversation Summary:</p>
                <p className="text-sm text-gray-700">{item.conversationSummary}</p>
              </div>

              {/* Assignment & Actions */}
              <div className="flex items-center justify-between pt-3 border-t border-gray-200">
                <div className="flex items-center gap-2">
                  {item.assignedTo ? (
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <User className="w-4 h-4" />
                      <span>Assigned to: <span className="font-medium">{item.assignedTo}</span></span>
                    </div>
                  ) : (
                    <button
                      onClick={() => handleAssign(item.id, 'Me')}
                      className="text-sm text-[#388E3C] hover:text-[#1B5E20] font-medium"
                    >
                      Assign to Me
                    </button>
                  )}
                </div>

                <div className="flex gap-2">
                  {item.status === 'new' && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleStatusChange(item.id, 'in-progress')}
                    >
                      Start Working
                    </Button>
                  )}
                  {item.status === 'in-progress' && (
                    <Button
                      size="sm"
                      className="bg-green-600 hover:bg-green-700 text-white"
                      onClick={() => handleStatusChange(item.id, 'completed')}
                    >
                      <CircleCheck className="w-4 h-4 mr-2" />
                      Mark Complete
                    </Button>
                  )}
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setSelectedItem(selectedItem === item.id ? null : item.id)}
                  >
                    {selectedItem === item.id ? 'Close' : 'View Details'}
                  </Button>
                </div>
              </div>

              {/* Expanded Details */}
              {selectedItem === item.id && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <p className="text-sm font-medium text-gray-700 mb-2">Follow-Up Notes:</p>
                  <textarea
                    className="w-full p-3 border border-gray-200 rounded-lg text-sm"
                    rows={3}
                    placeholder="Add notes about this follow-up..."
                  />
                  <div className="flex gap-2 mt-2">
                    <Button size="sm" className="bg-[#1B5E20] hover:bg-[#388E3C] text-white">
                      Save Notes
                    </Button>
                    <Button size="sm" variant="outline">
                      View Full Conversation
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredItems.length === 0 && (
        <div className="text-center py-12">
          <User className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">No follow-up requests found</p>
        </div>
      )}
    </div>
  );
};