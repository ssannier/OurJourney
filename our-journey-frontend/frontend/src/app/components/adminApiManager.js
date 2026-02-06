// REST API Manager for Admin Operations
// Handles all communication with the admin REST API Gateway

import { REST_API_URL } from './constants.jsx';

class AdminApiManager {
  constructor() {
    this.baseUrl = REST_API_URL;
  }

  // ============================================================================
  // HELPER METHODS
  // ============================================================================

  /**
   * Make a REST API request with error handling
   * @private
   */
  async makeRequest(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    
    try {
      console.log(`Making request to: ${url}`, options);
      
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      // Parse response
      const data = await response.json();

      // Check if request was successful
      if (!response.ok) {
        throw new Error(data.error || `HTTP ${response.status}: ${response.statusText}`);
      }

      console.log(`Request successful:`, data);
      return data;

    } catch (error) {
      console.error(`API Error for ${endpoint}:`, error);
      throw error;
    }
  }

  /**
   * Build query string from parameters object
   * @private
   */
  buildQueryString(params) {
    if (!params || Object.keys(params).length === 0) return '';
    
    const queryParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        queryParams.append(key, value);
      }
    });
    
    const queryString = queryParams.toString();
    return queryString ? `?${queryString}` : '';
  }

  // ============================================================================
  // CONVERSATION OPERATIONS
  // ============================================================================

  /**
   * Get all conversations with optional filtering and pagination
   * @param {Object} filters - Optional filters { flag, userId, county, limit, startKey }
   * @returns {Promise<Object>} { items: [...], count: number, nextPageKey?: string }
   */
  async getConversations(filters = {}) {
    const queryString = this.buildQueryString(filters);
    return await this.makeRequest(`/conversations${queryString}`, {
      method: 'GET',
    });
  }

  /**
   * Get a specific conversation by ID
   * @param {string} conversationId - Conversation ID
   * @returns {Promise<Object>} Conversation object
   */
  async getConversation(conversationId) {
    return await this.makeRequest(`/conversations/${conversationId}`, {
      method: 'GET',
    });
  }

  /**
   * Update a conversation's flag status
   * @param {string} conversationId - Conversation ID
   * @param {string} timestamp - Conversation timestamp (sort key)
   * @param {string} newFlag - New flag value (none/crisis/followup/resolved)
   * @returns {Promise<Object>} Updated conversation
   */
  async updateConversationFlag(conversationId, timestamp, newFlag) {
    return await this.makeRequest(`/conversations/${conversationId}`, {
      method: 'PUT',
      body: JSON.stringify({
        timestamp: timestamp,
        flag: newFlag,
      }),
    });
  }

  /**
   * Get conversations by flag with pagination
   * Convenience method for common filtering use case
   * @param {string} flag - Flag to filter by (crisis/followup/resolved/none)
   * @param {number} limit - Number of items per page (default 50)
   * @returns {Promise<Object>} Filtered conversations
   */
  async getConversationsByFlag(flag, limit = 50) {
    return await this.getConversations({ flag, limit });
  }

  // ============================================================================
  // FOLLOW-UP OPERATIONS
  // ============================================================================

  /**
   * Get all follow-ups with optional filtering and pagination
   * @param {Object} filters - Optional filters { status, priority, requestType, limit, startKey }
   * @returns {Promise<Object>} { items: [...], count: number, nextPageKey?: string }
   */
  async getFollowUps(filters = {}) {
    const queryString = this.buildQueryString(filters);
    return await this.makeRequest(`/followups${queryString}`, {
      method: 'GET',
    });
  }

  /**
   * Get a specific follow-up by ID
   * @param {string} followupId - Follow-up ID
   * @returns {Promise<Object>} Follow-up object
   */
  async getFollowUp(followupId) {
    return await this.makeRequest(`/followups/${followupId}`, {
      method: 'GET',
    });
  }

  /**
   * Update a follow-up's status, assignment, or notes
   * @param {string} followupId - Follow-up ID
   * @param {string} timestamp - Follow-up timestamp (sort key)
   * @param {Object} updates - Fields to update { status?, assignedTo?, notes? }
   * @returns {Promise<Object>} Updated follow-up
   */
  async updateFollowUp(followupId, timestamp, updates) {
    return await this.makeRequest(`/followups/${followupId}`, {
      method: 'PUT',
      body: JSON.stringify({
        timestamp: timestamp,
        ...updates,
      }),
    });
  }

  /**
   * Update follow-up status
   * Convenience method for status changes
   * @param {string} followupId - Follow-up ID
   * @param {string} timestamp - Follow-up timestamp
   * @param {string} newStatus - New status (new/in-progress/completed)
   * @returns {Promise<Object>} Updated follow-up
   */
  async updateFollowUpStatus(followupId, timestamp, newStatus) {
    return await this.updateFollowUp(followupId, timestamp, { status: newStatus });
  }

  /**
   * Assign a follow-up to a team member
   * Convenience method for assignments
   * @param {string} followupId - Follow-up ID
   * @param {string} timestamp - Follow-up timestamp
   * @param {string} assignee - Name of person to assign to
   * @returns {Promise<Object>} Updated follow-up
   */
  async assignFollowUp(followupId, timestamp, assignee) {
    return await this.updateFollowUp(followupId, timestamp, { assignedTo: assignee });
  }

  /**
   * Save notes for a follow-up
   * Convenience method for adding notes
   * @param {string} followupId - Follow-up ID
   * @param {string} timestamp - Follow-up timestamp
   * @param {string} notes - Notes to save
   * @returns {Promise<Object>} Updated follow-up
   */
  async saveFollowUpNotes(followupId, timestamp, notes) {
    return await this.updateFollowUp(followupId, timestamp, { notes });
  }

  /**
   * Get follow-ups by status with pagination
   * Convenience method for common filtering use case
   * @param {string} status - Status to filter by (new/in-progress/completed)
   * @param {number} limit - Number of items per page (default 50)
   * @returns {Promise<Object>} Filtered follow-ups
   */
  async getFollowUpsByStatus(status, limit = 50) {
    return await this.getFollowUps({ status, limit });
  }

  /**
   * Get urgent follow-ups
   * Convenience method for filtering urgent items
   * @param {number} limit - Number of items per page (default 50)
   * @returns {Promise<Object>} Urgent follow-ups
   */
  async getUrgentFollowUps(limit = 50) {
    return await this.getFollowUps({ priority: 'urgent', limit });
  }

  /**
   * Get crisis follow-ups
   * Convenience method for filtering crisis items
   * @param {number} limit - Number of items per page (default 50)
   * @returns {Promise<Object>} Crisis follow-ups
   */
  async getCrisisFollowUps(limit = 50) {
    return await this.getFollowUps({ requestType: 'crisis', limit });
  }

  // ============================================================================
  // PAGINATION HELPERS
  // ============================================================================

  /**
   * Load next page of conversations
   * @param {string} nextPageKey - Pagination key from previous response
   * @param {Object} filters - Same filters from initial request
   * @returns {Promise<Object>} Next page of conversations
   */
  async loadNextConversationsPage(nextPageKey, filters = {}) {
    return await this.getConversations({
      ...filters,
      startKey: nextPageKey,
    });
  }

  /**
   * Load next page of follow-ups
   * @param {string} nextPageKey - Pagination key from previous response
   * @param {Object} filters - Same filters from initial request
   * @returns {Promise<Object>} Next page of follow-ups
   */
  async loadNextFollowUpsPage(nextPageKey, filters = {}) {
    return await this.getFollowUps({
      ...filters,
      startKey: nextPageKey,
    });
  }

  // ============================================================================
  // BATCH OPERATIONS
  // ============================================================================

  /**
   * Get statistics for conversations
   * Fetches counts for each flag type
   * @returns {Promise<Object>} { total, crisis, followup, resolved, none }
   */
  async getConversationStats() {
    try {
      // Fetch all conversations (or use aggregation if available)
      const allConversations = await this.getConversations({ limit: 100 });
      
      const stats = {
        total: allConversations.count || 0,
        crisis: allConversations.items.filter(c => c.flag === 'crisis').length,
        followup: allConversations.items.filter(c => c.flag === 'followup').length,
        resolved: allConversations.items.filter(c => c.flag === 'resolved').length,
        none: allConversations.items.filter(c => c.flag === 'none').length,
      };

      return stats;
    } catch (error) {
      console.error('Error getting conversation stats:', error);
      throw error;
    }
  }

  /**
   * Get statistics for follow-ups
   * Fetches counts for each status and priority
   * @returns {Promise<Object>} { total, new, inProgress, completed, urgent }
   */
  async getFollowUpStats() {
    try {
      // Fetch all follow-ups (or use aggregation if available)
      const allFollowUps = await this.getFollowUps({ limit: 100 });
      
      const stats = {
        total: allFollowUps.count || 0,
        new: allFollowUps.items.filter(f => f.status === 'new').length,
        inProgress: allFollowUps.items.filter(f => f.status === 'in-progress').length,
        completed: allFollowUps.items.filter(f => f.status === 'completed').length,
        urgent: allFollowUps.items.filter(f => f.priority === 'urgent').length,
      };

      return stats;
    } catch (error) {
      console.error('Error getting follow-up stats:', error);
      throw error;
    }
  }
}

// Create singleton instance and export as default
const adminApiManager = new AdminApiManager();
export { adminApiManager as default };