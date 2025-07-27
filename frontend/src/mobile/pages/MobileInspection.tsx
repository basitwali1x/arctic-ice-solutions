import { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Textarea } from '../../components/ui/textarea';
import { Camera, CheckCircle, AlertTriangle, FileText, PenTool } from 'lucide-react';

interface InspectionItem {
  id: string;
  category: string;
  item: string;
  status: 'pass' | 'fail' | 'na' | null;
  notes?: string;
  photo?: string;
}

interface PreTripInspection {
  vehicle_id: string;
  driver_name: string;
  inspection_date: string;
  odometer_reading: number;
  fuel_level: number;
  items: InspectionItem[];
  driver_signature?: string;
  overall_status: 'pass' | 'fail' | 'incomplete';
}

export function MobileInspection() {
  const [inspection, setInspection] = useState<PreTripInspection>({
    vehicle_id: 'LA-ICE-01',
    driver_name: 'Field Technician',
    inspection_date: new Date().toISOString().split('T')[0],
    odometer_reading: 125430,
    fuel_level: 75,
    overall_status: 'incomplete',
    items: [
      { id: 'brakes-1', category: 'Brakes', item: 'Brake pedal feel and travel', status: null },
      { id: 'brakes-2', category: 'Brakes', item: 'Parking brake operation', status: null },
      { id: 'brakes-3', category: 'Brakes', item: 'Air brake system (if applicable)', status: null },
      
      { id: 'lights-1', category: 'Lights', item: 'Headlights (high/low beam)', status: null },
      { id: 'lights-2', category: 'Lights', item: 'Tail lights and brake lights', status: null },
      { id: 'lights-3', category: 'Lights', item: 'Turn signals and hazard lights', status: null },
      { id: 'lights-4', category: 'Lights', item: 'Clearance and marker lights', status: null },
      
      { id: 'tires-1', category: 'Tires', item: 'Tire condition and tread depth', status: null },
      { id: 'tires-2', category: 'Tires', item: 'Tire pressure (visual check)', status: null },
      { id: 'tires-3', category: 'Tires', item: 'Wheel nuts and rims', status: null },
      
      { id: 'engine-1', category: 'Engine', item: 'Oil level and condition', status: null },
      { id: 'engine-2', category: 'Engine', item: 'Coolant level', status: null },
      { id: 'engine-3', category: 'Engine', item: 'Belt condition', status: null },
      { id: 'engine-4', category: 'Engine', item: 'Battery and connections', status: null },
      
      { id: 'reefer-1', category: 'Refrigeration', item: 'Reefer unit operation', status: null },
      { id: 'reefer-2', category: 'Refrigeration', item: 'Temperature controls', status: null },
      { id: 'reefer-3', category: 'Refrigeration', item: 'Fuel level (reefer)', status: null },
      { id: 'reefer-4', category: 'Refrigeration', item: 'Door seals and gaskets', status: null },
      
      { id: 'safety-1', category: 'Safety', item: 'Fire extinguisher', status: null },
      { id: 'safety-2', category: 'Safety', item: 'First aid kit', status: null },
      { id: 'safety-3', category: 'Safety', item: 'Emergency triangles', status: null },
      { id: 'safety-4', category: 'Safety', item: 'Horn operation', status: null },
      { id: 'safety-5', category: 'Safety', item: 'Mirrors and visibility', status: null }
    ]
  });

  const signatureCanvasRef = useRef<HTMLCanvasElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);

  const updateInspectionItem = (itemId: string, status: 'pass' | 'fail' | 'na', notes?: string) => {
    setInspection(prev => ({
      ...prev,
      items: prev.items.map(item => 
        item.id === itemId ? { ...item, status, notes } : item
      )
    }));
  };

  const takePhoto = async (itemId: string) => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      const video = document.createElement('video');
      video.srcObject = stream;
      video.play();

      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d');
      
      setTimeout(() => {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context?.drawImage(video, 0, 0);
        
        const photoData = canvas.toDataURL('image/jpeg');
        setInspection(prev => ({
          ...prev,
          items: prev.items.map(item => 
            item.id === itemId ? { ...item, photo: photoData } : item
          )
        }));
        
        stream.getTracks().forEach(track => track.stop());
        alert('Photo captured successfully!');
      }, 3000);
      
    } catch (error) {
      console.error('Camera error:', error);
      alert('Camera not available. Please check permissions.');
    }
  };

  useEffect(() => {
    const canvas = signatureCanvasRef.current;
    if (canvas) {
      const context = canvas.getContext('2d');
      if (context) {
        context.strokeStyle = '#000';
        context.lineWidth = 2;
        context.lineCap = 'round';
      }
    }
  }, []);

  const startDrawing = (e: React.MouseEvent<HTMLCanvasElement>) => {
    setIsDrawing(true);
    const canvas = e.currentTarget;
    const rect = canvas.getBoundingClientRect();
    const context = canvas.getContext('2d');
    if (context) {
      context.beginPath();
      context.moveTo(e.clientX - rect.left, e.clientY - rect.top);
    }
  };

  const draw = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDrawing) return;
    const canvas = e.currentTarget;
    const rect = canvas.getBoundingClientRect();
    const context = canvas.getContext('2d');
    if (context) {
      context.lineTo(e.clientX - rect.left, e.clientY - rect.top);
      context.stroke();
    }
  };

  const stopDrawing = () => {
    setIsDrawing(false);
  };

  const clearSignature = () => {
    const canvas = signatureCanvasRef.current;
    if (canvas) {
      const context = canvas.getContext('2d');
      if (context) {
        context.clearRect(0, 0, canvas.width, canvas.height);
      }
    }
  };

  const submitInspection = () => {
    const failedItems = inspection.items.filter(item => item.status === 'fail');
    const incompleteItems = inspection.items.filter(item => item.status === null);
    
    if (incompleteItems.length > 0) {
      alert(`Please complete all inspection items. ${incompleteItems.length} items remaining.`);
      return;
    }

    const overallStatus = failedItems.length > 0 ? 'fail' : 'pass';
    
    const signatureData = signatureCanvasRef.current?.toDataURL();
    
    const finalInspection = {
      ...inspection,
      overall_status: overallStatus,
      driver_signature: signatureData,
      completed_at: new Date().toISOString()
    };

    console.log('Submitting inspection:', finalInspection);
    alert(`Pre-trip inspection ${overallStatus === 'pass' ? 'PASSED' : 'FAILED'}. ${failedItems.length > 0 ? 'Please address failed items before departure.' : 'Vehicle cleared for operation.'}`);
  };


  const getStatusIcon = (status: string | null) => {
    switch (status) {
      case 'pass': return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'fail': return <AlertTriangle className="h-4 w-4 text-red-600" />;
      case 'na': return <span className="text-gray-600">N/A</span>;
      default: return <span className="text-gray-400">-</span>;
    }
  };

  const groupedItems = inspection.items.reduce((acc, item) => {
    if (!acc[item.category]) acc[item.category] = [];
    acc[item.category].push(item);
    return acc;
  }, {} as Record<string, InspectionItem[]>);

  const completedItems = inspection.items.filter(item => item.status !== null).length;
  const totalItems = inspection.items.length;
  const progressPercentage = (completedItems / totalItems) * 100;

  return (
    <div className="p-4 space-y-4">
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4">Pre-Trip Inspection</h2>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Vehicle {inspection.vehicle_id}</span>
            <Badge variant="outline">
              {completedItems}/{totalItems} Complete
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                style={{ width: `${progressPercentage}%` }}
              ></div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="odometer">Odometer Reading</Label>
                <Input
                  id="odometer"
                  type="number"
                  value={inspection.odometer_reading}
                  onChange={(e) => setInspection({...inspection, odometer_reading: parseInt(e.target.value)})}
                />
              </div>
              <div>
                <Label htmlFor="fuel">Fuel Level (%)</Label>
                <Input
                  id="fuel"
                  type="number"
                  value={inspection.fuel_level}
                  onChange={(e) => setInspection({...inspection, fuel_level: parseInt(e.target.value)})}
                />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {Object.entries(groupedItems).map(([category, items]) => (
        <Card key={category}>
          <CardHeader>
            <CardTitle className="text-lg">{category}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {items.map((item) => (
                <div key={item.id} className="border rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium">{item.item}</span>
                    {getStatusIcon(item.status)}
                  </div>
                  <div className="flex space-x-2 mb-2">
                    <Button
                      size="sm"
                      variant={item.status === 'pass' ? 'default' : 'outline'}
                      onClick={() => updateInspectionItem(item.id, 'pass')}
                    >
                      Pass
                    </Button>
                    <Button
                      size="sm"
                      variant={item.status === 'fail' ? 'destructive' : 'outline'}
                      onClick={() => updateInspectionItem(item.id, 'fail')}
                    >
                      Fail
                    </Button>
                    <Button
                      size="sm"
                      variant={item.status === 'na' ? 'secondary' : 'outline'}
                      onClick={() => updateInspectionItem(item.id, 'na')}
                    >
                      N/A
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => takePhoto(item.id)}
                    >
                      <Camera className="h-3 w-3 mr-1" />
                      Photo
                    </Button>
                  </div>
                  {(item.status === 'fail' || item.notes) && (
                    <Textarea
                      placeholder="Add notes for this item..."
                      value={item.notes || ''}
                      onChange={(e) => updateInspectionItem(item.id, item.status!, e.target.value)}
                      className="mt-2"
                    />
                  )}
                  {item.photo && (
                    <div className="mt-2">
                      <img src={item.photo} alt="Inspection photo" className="w-20 h-20 object-cover rounded" />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ))}

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <PenTool className="h-5 w-5 mr-2" />
            Driver Signature
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <canvas
              ref={signatureCanvasRef}
              width={300}
              height={150}
              className="border border-gray-300 rounded w-full"
              style={{ touchAction: 'none' }}
              onMouseDown={startDrawing}
              onMouseMove={draw}
              onMouseUp={stopDrawing}
              onMouseLeave={stopDrawing}
            />
            <div className="flex space-x-2">
              <Button variant="outline" onClick={clearSignature}>
                Clear Signature
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="flex space-x-2">
        <Button 
          onClick={submitInspection} 
          className="flex-1"
          disabled={completedItems < totalItems}
        >
          <FileText className="h-4 w-4 mr-2" />
          Submit Inspection
        </Button>
      </div>
    </div>
  );
}
