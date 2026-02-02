import { useState } from 'react';
import { Search, ListFilter, Eye, Flag, CircleCheck, MessageSquare } from 'lucide-react';
import { Input } from '../ui/input';
import { Button } from '../ui/button';
import { Card, CardContent } from '../ui/card';
import { Badge } from '../ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';

const flagColors = {
  'none': 'bg-gray-100 text-gray-600',
  'crisis': 'bg-red-100 text-red-700',
  'followup': 'bg-amber-100 text-amber-700',
  'resolved': 'bg-green-100 text-green-700'
};

const flagLabels = {
  'none': 'Normal',
  'crisis': 'Crisis',
  'followup': 'Follow-up',
  'resolved': 'Resolved'
};

export const ConversationsView = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterFlag, setFilterFlag] = useState('all');
  const [selectedConv, setSelectedConv] = useState<string | null>(null);

  const conversations: any[] = [];

  const filteredConversations = conversations.filter(conv => {
    const matchesSearch = conv.userId.includes(searchTerm) || 
                          conv.county.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          conv.id.includes(searchTerm);
    const matchesFilter = filterFlag === 'all' || conv.flag === filterFlag;
    return matchesSearch && matchesFilter;
  });

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 60) return `${diffMins} min ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)} hours ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-gray-900 mb-2">Conversation History</h2>
        <p className="text-gray-600">View and manage user conversations</p>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <Input
            placeholder="Search by user ID, county, or conversation ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select value={filterFlag} onValueChange={setFilterFlag}>
          <SelectTrigger className="w-48">
            <ListFilter className="w-4 h-4 mr-2" />
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Conversations</SelectItem>
            <SelectItem value="crisis">Crisis</SelectItem>
            <SelectItem value="followup">Follow-up</SelectItem>
            <SelectItem value="resolved">Resolved</SelectItem>
            <SelectItem value="none">Normal</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Conversations List */}
      <div className="grid grid-cols-1 gap-3">
        {filteredConversations.map((conv) => (
          <Card 
            key={conv.id}
            className={`cursor-pointer transition-all hover:shadow-md ${
              selectedConv === conv.id ? 'ring-2 ring-[#388E3C]' : ''
            }`}
            onClick={() => setSelectedConv(selectedConv === conv.id ? null : conv.id)}
          >
            <CardContent className="p-4">
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-semibold text-gray-900">{conv.userId}</h3>
                    <Badge className={flagColors[conv.flag as keyof typeof flagColors]}>
                      {flagLabels[conv.flag as keyof typeof flagLabels]}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600">{conv.county} County • {conv.messageCount} messages</p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-gray-500">{formatTime(conv.timestamp)}</p>
                  <p className="text-xs text-gray-400 mt-1">{conv.id}</p>
                </div>
              </div>

              <p className="text-sm text-gray-700 italic mb-2">"{conv.lastMessage}"</p>

              <div className="flex items-center gap-2">
                {conv.categories.map((cat: string) => (
                  <span 
                    key={cat}
                    className="text-xs bg-[#E8F5E9] text-[#1B5E20] px-2 py-1 rounded"
                  >
                    {cat}
                  </span>
                ))}
              </div>

              {selectedConv === conv.id && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline" className="flex-1">
                      <Eye className="w-4 h-4 mr-2" />
                      View Full Transcript
                    </Button>
                    {conv.flag !== 'resolved' && (
                      <Button size="sm" variant="outline" className="text-green-600 hover:text-green-700">
                        <CircleCheck className="w-4 h-4 mr-2" />
                        Mark Resolved
                      </Button>
                    )}
                    {conv.flag === 'none' && (
                      <Button size="sm" variant="outline" className="text-amber-600 hover:text-amber-700">
                        <Flag className="w-4 h-4 mr-2" />
                        Flag for Review
                      </Button>
                    )}
                  </div>
                  
                  {/* Mock transcript preview */}
                  <div className="mt-4 p-3 bg-gray-50 rounded-lg max-h-48 overflow-y-auto">
                    <p className="text-xs text-gray-500 mb-2">Conversation Preview:</p>
                    <div className="space-y-2">
                      <div className="text-sm">
                        <span className="font-medium text-[#388E3C]">JoJo:</span> Hi! What can I help you with today?
                      </div>
                      <div className="text-sm">
                        <span className="font-medium text-gray-700">{conv.userId}:</span> {conv.lastMessage}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredConversations.length === 0 && (
        <div className="text-center py-12">
          <MessageSquare className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">No conversations found matching your filters</p>
        </div>
      )}
    </div>
  );
};