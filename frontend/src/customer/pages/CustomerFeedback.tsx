import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Input } from '../../components/ui/input';
import { Star, Send } from 'lucide-react';

interface CustomerFeedback {
  id: string;
  customerId: string;
  orderId?: string;
  type: 'delivery' | 'product' | 'service' | 'complaint' | 'suggestion';
  rating: 1 | 2 | 3 | 4 | 5;
  subject: string;
  message: string;
  submittedAt: string;
  status: string;
  response?: string;
}

export function CustomerFeedback() {
  const [feedback, setFeedback] = useState<CustomerFeedback[]>([]);
  const [newFeedback, setNewFeedback] = useState<{
    type: 'delivery' | 'product' | 'service' | 'complaint' | 'suggestion';
    rating: 1 | 2 | 3 | 4 | 5;
    subject: string;
    message: string;
    orderId: string;
  }>({
    type: 'delivery',
    rating: 5,
    subject: '',
    message: '',
    orderId: ''
  });

  useEffect(() => {
    const mockFeedback: CustomerFeedback[] = [
      {
        id: 'feedback-001',
        customerId: 'cust-001',
        type: 'delivery',
        rating: 5,
        subject: 'Great service!',
        message: 'Driver was very professional and on time.',
        submittedAt: '2024-01-15T10:30:00Z',
        status: 'resolved',
        response: 'Thank you for your feedback! We appreciate your business.'
      }
    ];
    setFeedback(mockFeedback);
  }, []);

  const submitFeedback = () => {
    if (!newFeedback.subject || !newFeedback.message) {
      alert('Please fill in all feedback fields');
      return;
    }

    const feedbackItem: CustomerFeedback = {
      id: `feedback-${Date.now()}`,
      customerId: 'cust-001',
      orderId: newFeedback.orderId || undefined,
      type: newFeedback.type,
      rating: newFeedback.rating,
      subject: newFeedback.subject,
      message: newFeedback.message,
      submittedAt: new Date().toISOString(),
      status: 'new'
    };

    setFeedback(prev => [feedbackItem, ...prev]);
    setNewFeedback({
      type: 'delivery',
      rating: 5,
      subject: '',
      message: '',
      orderId: ''
    });
    
    alert('Feedback submitted successfully!');
  };

  return (
    <div className="p-4 space-y-4">
      <div>
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Feedback</h2>
      </div>

      <Card className="dark:bg-gray-800 dark:border-gray-700">
        <CardHeader>
          <CardTitle className="text-gray-900 dark:text-white">Submit Feedback</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1 text-gray-900 dark:text-white">Feedback Type</label>
            <select
              value={newFeedback.type}
              onChange={(e) => setNewFeedback(prev => ({ ...prev, type: e.target.value as 'delivery' | 'product' | 'service' | 'complaint' | 'suggestion' }))}
              className="w-full p-2 border dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white"
            >
              <option value="delivery">Delivery</option>
              <option value="product">Product Quality</option>
              <option value="service">Customer Service</option>
              <option value="complaint">Complaint</option>
              <option value="suggestion">Suggestion</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1 text-gray-900 dark:text-white">Rating</label>
            <div className="flex space-x-1">
              {[1, 2, 3, 4, 5].map((rating) => (
                <Button
                  key={rating}
                  variant={newFeedback.rating >= rating ? "default" : "outline"}
                  size="sm"
                  onClick={() => setNewFeedback(prev => ({ ...prev, rating: rating as 1 | 2 | 3 | 4 | 5 }))}
                >
                  <Star className="w-4 h-4" />
                </Button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1 text-gray-900 dark:text-white">Subject</label>
            <Input
              value={newFeedback.subject}
              onChange={(e) => setNewFeedback(prev => ({ ...prev, subject: e.target.value }))}
              placeholder="Brief subject line"
              autoComplete="off"
              className="dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1 text-gray-900 dark:text-white">Message</label>
            <textarea
              value={newFeedback.message}
              onChange={(e) => setNewFeedback(prev => ({ ...prev, message: e.target.value }))}
              placeholder="Your detailed feedback"
              className="w-full p-2 border dark:border-gray-600 rounded-md h-24 dark:bg-gray-700 dark:text-white"
            />
          </div>

          <Button className="w-full" onClick={submitFeedback}>
            <Send className="w-4 h-4 mr-2" />
            Submit Feedback
          </Button>
        </CardContent>
      </Card>

      <Card className="dark:bg-gray-800 dark:border-gray-700">
        <CardHeader>
          <CardTitle className="text-gray-900 dark:text-white">Previous Feedback</CardTitle>
        </CardHeader>
        <CardContent>
          {feedback.length === 0 ? (
            <p className="text-center text-gray-500 dark:text-gray-400 py-4">No feedback submitted yet</p>
          ) : (
            <div className="space-y-3">
              {feedback.map((item) => (
                <div key={item.id} className="border dark:border-gray-600 rounded-lg p-3">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">{item.subject}</p>
                      <div className="flex items-center space-x-1">
                        {[1, 2, 3, 4, 5].map((star) => (
                          <Star
                            key={star}
                            className={`w-3 h-3 ${star <= item.rating ? 'text-yellow-400 fill-current' : 'text-gray-300 dark:text-gray-600'}`}
                          />
                        ))}
                      </div>
                    </div>
                    <Badge variant={item.status === 'resolved' ? 'default' : 'secondary'}>
                      {item.status}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-300">{item.message}</p>
                  {item.response && (
                    <div className="mt-2 p-2 bg-green-50 dark:bg-green-900/20 rounded">
                      <p className="text-sm text-gray-900 dark:text-white"><strong>Response:</strong> {item.response}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
