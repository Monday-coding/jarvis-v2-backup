-- Agents
DELETE FROM agents;
INSERT INTO agents (agent_id, name, model, provider, workspace, is_active, created_at, updated_at, metadata) VALUES ('main', 'Main Agent', 'zai/glm-4.7', 'zai', '~/.openclaw/workspace', 2026-02-25 05:01:19, '2026-02-25 05:01:19', '{"role": "orchestrator"}', '1');
INSERT INTO agents (agent_id, name, model, provider, workspace, is_active, created_at, updated_at, metadata) VALUES ('classifier', 'Classifier', 'ollama/qwen2.5:1.5b', 'ollama', '~/.openclaw/workspace-classifier', 2026-02-25 05:01:19, '2026-02-25 05:01:19', '{"role": "classifier"}', '1');
INSERT INTO agents (agent_id, name, model, provider, workspace, is_active, created_at, updated_at, metadata) VALUES ('chat', 'Chat Agent', 'zai/glm-4.7-flashx', 'zai', '~/.openclaw/workspace-chat', 2026-02-25 05:01:19, '2026-02-25 05:01:19', '{"role": "chat"}', '1');
INSERT INTO agents (agent_id, name, model, provider, workspace, is_active, created_at, updated_at, metadata) VALUES ('task', 'Task Agent', 'zai/glm-4.7-flash', 'zai', '~/.openclaw/workspace-task', 2026-02-25 05:01:19, '2026-02-25 05:01:19', '{"role": "task"}', '1');
INSERT INTO agents (agent_id, name, model, provider, workspace, is_active, created_at, updated_at, metadata) VALUES ('coding', 'Coding Agent', 'zai/glm-4.7', 'zai', '~/.openclaw/workspace-coding', 2026-02-25 05:01:19, '2026-02-25 05:01:19', '{"role": "coding"}', '1');
INSERT INTO agents (agent_id, name, model, provider, workspace, is_active, created_at, updated_at, metadata) VALUES ('data', 'Data Agent', 'zai/glm-4.7-flashx', 'zai', '~/.openclaw/workspace-data', 2026-02-25 05:01:19, '2026-02-25 05:01:19', '{"role": "data"}', '1');
INSERT INTO agents (agent_id, name, model, provider, workspace, is_active, created_at, updated_at, metadata) VALUES ('qa', 'QA Agent', 'zai/glm-4.7-flash', 'zai', '~/.openclaw/workspace-qa', 2026-02-25 05:01:19, '2026-02-25 05:01:19', '{"role": "qa"}', '1');

-- Knowledge Base
DELETE FROM knowledge_base;

-- Memory
DELETE FROM memory;

-- Logs
DELETE FROM logs;
