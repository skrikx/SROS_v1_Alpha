const API_BASE_URL = '/api';

export interface Agent {
    name: string;
    role: string;
}

export interface Task {
    task_id: string;
    status: string;
    result?: any;
}

export interface LogEntry {
    timestamp: string;
    level: string;
    message: string;
    [key: string]: any;
}

export interface KnowledgePack {
    id: string;
    name: string;
    content: any;
    metadata: any;
}

export const api = {
    getAgents: async (): Promise<Agent[]> => {
        const response = await fetch(`${API_BASE_URL}/agents`);
        const data = await response.json();
        return data.agents;
    },

    runAgent: async (agentName: string, task: string): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/agents/run`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ agent_name: agentName, task }),
        });
        return response.json();
    },

    getRouterTasks: async (): Promise<Task[]> => {
        const response = await fetch(`${API_BASE_URL}/router/tasks`);
        const data = await response.json();
        return data.tasks;
    },

    submitRoutedTask: async (task: string): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/router/tasks`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ agent_name: 'router', task }),
        });
        return response.json();
    },

    getLogs: async (): Promise<LogEntry[]> => {
        const response = await fetch(`${API_BASE_URL}/logs`);
        const data = await response.json();
        return data.logs;
    },

    getKernelStatus: async (): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/status`);
        return response.json();
    },

    getDaemonStatus: async (): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/kernel/daemons`);
        return response.json();
    },

    triggerEvolution: async (): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/evolution/cycle`, {
            method: 'POST',
        });
        return response.json();
    },

    getEvolutionStatus: async (): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/evolution/status`);
        return response.json();
    },

    getKnowledgePacks: async (): Promise<KnowledgePack[]> => {
        const response = await fetch(`${API_BASE_URL}/knowledge/packs`);
        const data = await response.json();
        return data.packs;
    },

    searchKnowledge: async (query: string): Promise<KnowledgePack[]> => {
        const response = await fetch(`${API_BASE_URL}/knowledge/search?query=${encodeURIComponent(query)}`);
        const data = await response.json();
        return data.results;
    },

    skrikxChat: async (message: string, context?: any): Promise<any> => {
        const response = await fetch(`${API_BASE_URL}/skrikx/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, context }),
        });
        return response.json();
    }
};
