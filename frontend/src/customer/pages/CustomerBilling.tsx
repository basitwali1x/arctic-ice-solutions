import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { DollarSign, Download } from 'lucide-react';

interface Invoice {
  id: string;
  invoiceNumber: string;
  dueDate: string;
  status: string;
  totalAmount: number;
}

export function CustomerBilling() {
  const [invoices, setInvoices] = useState<Invoice[]>([]);

  useEffect(() => {
    const mockInvoices: Invoice[] = [
      {
        id: 'inv-001',
        invoiceNumber: 'INV-001',
        dueDate: '2024-02-15',
        status: 'paid',
        totalAmount: 46.80
      },
      {
        id: 'inv-002',
        invoiceNumber: 'INV-002',
        dueDate: '2024-02-20',
        status: 'pending',
        totalAmount: 125.50
      }
    ];
    setInvoices(mockInvoices);
  }, []);

  const handleDownloadInvoice = async (invoiceId: string) => {
    try {
      const response = await fetch(`/api/invoices/${invoiceId}/download`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to download invoice');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `invoice_${invoiceId}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading invoice:', error);
      alert('Failed to download invoice. Please try again.');
    }
  };

  return (
    <div className="p-4 space-y-4">
      <div>
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Billing & Invoices</h2>
      </div>

      <Card className="dark:bg-gray-800 dark:border-gray-700">
        <CardHeader>
          <CardTitle className="flex items-center text-gray-900 dark:text-white">
            <DollarSign className="w-5 h-5 mr-2" />
            Invoices & Billing
          </CardTitle>
        </CardHeader>
        <CardContent>
          {invoices.length === 0 ? (
            <p className="text-center text-gray-500 dark:text-gray-400 py-4">No invoices available</p>
          ) : (
            <div className="space-y-3">
              {invoices.map((invoice) => (
                <div key={invoice.id} className="border dark:border-gray-600 rounded-lg p-3">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">Invoice #{invoice.invoiceNumber}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-300">Due: {invoice.dueDate}</p>
                    </div>
                    <Badge variant={invoice.status === 'paid' ? 'default' : 'destructive'}>
                      {invoice.status}
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="font-medium text-gray-900 dark:text-white">${invoice.totalAmount.toFixed(2)}</span>
                    <Button size="sm" variant="outline" onClick={() => handleDownloadInvoice(invoice.id)}>
                      <Download className="w-4 h-4 mr-1" />
                      Download
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
