import { create } from 'zustand'

interface AgentEvent {
  type: string;
  agent_id: string;
  data: any;
  timestamp: number;
}

interface AgentState {
  status: string;
  full_text: string;
  agent_type: string;
  thinking_message: string;
  tool_calls: { tool: string; input: any; result?: any; sources?: string[]; status: 'running' | 'done' | 'error' }[];
  sources: string[];
  queries_used: string[];
  [key: string]: any;
}

interface StreamState {
  events: AgentEvent[];
  activeAgents: Record<string, AgentState>;
  addEvent: (event: Omit<AgentEvent, 'timestamp'>) => void;
  clearEvents: () => void;
}

export const useStreamStore = create<StreamState>((set) => ({
  events: [],
  activeAgents: {},
  addEvent: (eventData) => set((state) => {
    const event = { ...eventData, timestamp: Date.now() };
    const agentId = event.agent_id;
    const currentAgent = state.activeAgents[agentId] || {
      status: 'spawned', full_text: '', agent_type: 'AGENT',
      thinking_message: '', tool_calls: [], sources: [], queries_used: []
    };
    
    let updatedAgent = { ...currentAgent, tool_calls: [...(currentAgent.tool_calls || [])] };
    
    if (event.type === 'stream_token') {
      updatedAgent.full_text += event.data.token;
      updatedAgent.thinking_message = ''; // Clear thinking when streaming starts
    } else if (event.type === 'status_update') {
      updatedAgent.status = event.data.status;
    } else if (event.type === 'AGENT_START') {
      updatedAgent.agent_type = event.data.agent_type || 'AGENT';
      updatedAgent.status = 'active';
    } else if (event.type === 'THINKING') {
      updatedAgent.thinking_message = event.data.message || '';
    } else if (event.type === 'TOOL_CALL') {
      updatedAgent.tool_calls.push({
        tool: event.data.tool,
        input: event.data.input,
        status: 'running'
      });
      updatedAgent.thinking_message = '';
    } else if (event.type === 'TOOL_RESULT') {
      const toolCalls = [...updatedAgent.tool_calls].reverse();
      const lastCall = toolCalls.find((t: any) => t.tool === event.data.tool && t.status === 'running');
      if (lastCall) {
        lastCall.result = event.data.result;
        lastCall.sources = event.data.sources || [];
        lastCall.status = 'done';
      }
    } else if (event.type === 'DONE') {
      updatedAgent.sources = event.data.sources || [];
      updatedAgent.queries_used = event.data.queries_used || [];
      updatedAgent.thinking_message = '';
    } else if (event.type === 'error') {
      updatedAgent.status = 'error';
      updatedAgent.full_text = '⚠️ Fatal Error: ' + (event.data.message || 'Unknown error occurred.');
      updatedAgent.thinking_message = '';
    } else {
      updatedAgent = { ...updatedAgent, ...event.data };
    }

    return { 
      events: [...state.events, event],
      activeAgents: {
        ...state.activeAgents,
        [agentId]: updatedAgent
      }
    };
  }),
  clearEvents: () => set({ events: [], activeAgents: {} }),
}))
