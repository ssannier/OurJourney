import { useState, useEffect } from 'react';
import { Search, ListFilter, Eye, Flag, CircleCheck, MessageSquare, Loader2, AlertCircle } from 'lucide-react';
import { Input } from '../ui/input';
import { Button } from '../ui/button';
import { Card, CardContent } from '../ui/card';
import { Badge } from '../ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import adminApiManager from '../adminApiManager';

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
  const [conversations, setConversations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  // Fetch conversations on mount and when filter changes
  useEffect(() => {
    fetchConversations();
  }, [filterFlag]);

  const fetchConversations = async () => {
    try {
      setLoading(true);
      setError(null);

      let data;
      if (filterFlag === 'all') {
        data = await adminApiManager.getConversations({ limit: 100 });
      } else {
        data = await adminApiManager.getConversationsByFlag(filterFlag, 100);
      }

      setConversations(data.items || []);
    } catch (err: any) {
      console.error('Error fetching conversations:', err);
      setError(err.message || 'Failed to load conversations');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateFlag = async (conv: any, newFlag: string) => {
    try {
      setActionLoading(conv.id);
      await adminApiManager.updateConversationFlag(conv.id, conv.timestamp, newFlag);
      
      // Refresh conversations after update
      await fetchConversations();
    } catch (err: any) {
      console.error('Error updating flag:', err);
      alert('Failed to update conversation: ' + err.message);
    } finally {
      setActionLoading(null);
    }
  };

  const filteredConversations = conversations.filter(conv => {
    const matchesSearch = conv.userId?.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          conv.county?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          conv.id?.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
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

  const renderTranscript = (messages: any[]) => {
    if (!messages || messages.length === 0) {
      return <p className="text-sm text-gray-500">No messages available</p>;
    }

    return (
      <div className="space-y-2">
        {messages.map((msg, idx) => {
          const isUser = msg.role === 'user';
          const text = Array.isArray(msg.content) 
            ? msg.content[0]?.text || '' 
            : msg.content || '';

          return (
            <div key={idx} className="text-sm">
              <span className={`font-medium ${isUser ? 'text-gray-700' : 'text-[#388E3C]'}`}>
                {isUser ? 'User' : 'JoJo'}:
              </span>{' '}
              <span className="text-gray-600">{text}</span>
            </div>
          );
        })}
      </div>
    );
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

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 text-[#388E3C] animate-spin" />
          <p className="ml-3 text-gray-600">Loading conversations...</p>
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-red-800 font-medium">Error loading conversations</p>
            <p className="text-red-700 text-sm mt-1">{error}</p>
            <Button 
              size="sm" 
              variant="outline" 
              className="mt-2"
              onClick={fetchConversations}
            >
              Try Again
            </Button>
          </div>
        </div>
      )}

      {/* Conversations List */}
      {!loading && !error && (
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
                      <h3 className="font-semibold text-gray-900">{conv.userId || 'Unknown User'}</h3>
                      <Badge className={flagColors[conv.flag as keyof typeof flagColors]}>
                        {flagLabels[conv.flag as keyof typeof flagLabels]}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600">
                      {conv.county || 'Unknown'} County • {conv.messageCount || 0} messages
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-gray-500">{formatTime(conv.timestamp)}</p>
                    <p className="text-xs text-gray-400 mt-1 font-mono">{conv.id}</p>
                  </div>
                </div>

                <p className="text-sm text-gray-700 italic mb-2">"{conv.lastMessage || 'No preview available'}"</p>

                {conv.categories && conv.categories.length > 0 && (
                  <div className="flex items-center gap-2 flex-wrap">
                    {conv.categories.map((cat: string) => (
                      <span 
                        key={cat}
                        className="text-xs bg-[#E8F5E9] text-[#1B5E20] px-2 py-1 rounded"
                      >
                        {cat}
                      </span>
                    ))}
                  </div>
                )}

                {selectedConv === conv.id && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <div className="flex gap-2 mb-4">
                      {conv.flag !== 'resolved' && (
                        <Button 
                          size="sm" 
                          variant="outline" 
                          className="text-green-600 hover:text-green-700"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleUpdateFlag(conv, 'resolved');
                          }}
                          disabled={actionLoading === conv.id}
                        >
                          {actionLoading === conv.id ? (
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          ) : (
                            <CircleCheck className="w-4 h-4 mr-2" />
                          )}
                          Mark Resolved
                        </Button>
                      )}
                      {conv.flag === 'none' && (
                        <Button 
                          size="sm" 
                          variant="outline" 
                          className="text-amber-600 hover:text-amber-700"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleUpdateFlag(conv, 'followup');
                          }}
                          disabled={actionLoading === conv.id}
                        >
                          {actionLoading === conv.id ? (
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          ) : (
                            <Flag className="w-4 h-4 mr-2" />
                          )}
                          Flag for Review
                        </Button>
                      )}
                      {conv.flag === 'followup' && (
                        <Button 
                          size="sm" 
                          variant="outline" 
                          className="text-red-600 hover:text-red-700"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleUpdateFlag(conv, 'crisis');
                          }}
                          disabled={actionLoading === conv.id}
                        >
                          {actionLoading === conv.id ? (
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          ) : (
                            <Flag className="w-4 h-4 mr-2" />
                          )}
                          Mark as Crisis
                        </Button>
                      )}
                    </div>
                    
                    {/* Full Transcript */}
                    <div className="p-3 bg-gray-50 rounded-lg max-h-96 overflow-y-auto">
                      <p className="text-xs text-gray-500 mb-3 font-medium">Full Conversation:</p>
                      {renderTranscript(conv.messages)}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {!loading && !error && filteredConversations.length === 0 && (
        <div className="text-center py-12">
          <MessageSquare className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">No conversations found matching your filters</p>
        </div>
      )}
    </div>
  );
};