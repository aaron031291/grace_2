import { useState } from 'react';
import { Surface, Card, CardHeader, CardContent, Button, Tag } from '../design-system';
import { MissionControlDashboard } from '../components/MissionControlDashboard';
import { Play, Filter, RefreshCw } from 'lucide-react';
import './TasksMissionsPage.css';

export function TasksMissionsPage() {
  const [filter, setFilter] = useState<'all' | 'missions' | 'background'>('all');

  const handleSelfHealing = () => {
    console.log('Triggering self-healing...');
    // TODO: Implement self-healing trigger
  };

  return (
    <Surface>
      <div className="tasks-missions-page">
        <div className="tasks-missions-page__header">
          <div>
            <h1 className="tasks-missions-page__title">Tasks & Missions Dashboard</h1>
            <p className="tasks-missions-page__subtitle">
              Track mission execution and background job orchestration
            </p>
          </div>
          <div className="tasks-missions-page__actions">
            <Button 
              variant="secondary" 
              icon={<RefreshCw size={18} />}
              onClick={handleSelfHealing}
            >
              Trigger Self-Healing
            </Button>
            <Button icon={<Play size={18} />}>
              Start New Mission
            </Button>
          </div>
        </div>

        <div className="tasks-missions-page__filters">
          <Button
            variant={filter === 'all' ? 'primary' : 'ghost'}
            size="sm"
            onClick={() => setFilter('all')}
            icon={<Filter size={16} />}
          >
            All Tasks
          </Button>
          <Button
            variant={filter === 'missions' ? 'primary' : 'ghost'}
            size="sm"
            onClick={() => setFilter('missions')}
          >
            Missions Only
          </Button>
          <Button
            variant={filter === 'background' ? 'primary' : 'ghost'}
            size="sm"
            onClick={() => setFilter('background')}
          >
            Background Jobs
          </Button>
        </div>

        <Card variant="bordered">
          <CardHeader>
            Mission Control Board
            <Tag variant="info">{filter.toUpperCase()}</Tag>
          </CardHeader>
          <CardContent className="tasks-missions-page__board">
            <MissionControlDashboard isOpen={true} onClose={() => {}} />
          </CardContent>
        </Card>
      </div>
    </Surface>
  );
}
