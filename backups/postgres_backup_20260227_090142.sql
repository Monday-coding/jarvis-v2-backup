--
-- PostgreSQL database dump
--

\restrict w1mE7sGcCiPxngAcYKnw0iTZf0pIkM8h9dLOiZxxaZRFWV7sypdMqwlUI6rTxBf

-- Dumped from database version 15.16
-- Dumped by pg_dump version 15.16

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: agents; Type: TABLE; Schema: public; Owner: openclaw
--

CREATE TABLE public.agents (
    id integer NOT NULL,
    agent_id character varying(50) NOT NULL,
    name character varying(100) NOT NULL,
    model character varying(100) NOT NULL,
    provider character varying(50) NOT NULL,
    workspace character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    is_active boolean DEFAULT true,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE public.agents OWNER TO openclaw;

--
-- Name: TABLE agents; Type: COMMENT; Schema: public; Owner: openclaw
--

COMMENT ON TABLE public.agents IS 'OpenClaw Agents 配置信息';


--
-- Name: agents_id_seq; Type: SEQUENCE; Schema: public; Owner: openclaw
--

CREATE SEQUENCE public.agents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.agents_id_seq OWNER TO openclaw;

--
-- Name: agents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: openclaw
--

ALTER SEQUENCE public.agents_id_seq OWNED BY public.agents.id;


--
-- Name: conversation_optimizations; Type: TABLE; Schema: public; Owner: openclaw
--

CREATE TABLE public.conversation_optimizations (
    id integer NOT NULL,
    optimization_id character varying(100) NOT NULL,
    conversation_id character varying(100) NOT NULL,
    optimization_type character varying(50) NOT NULL,
    optimization_date timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    before_metrics jsonb NOT NULL,
    after_metrics jsonb NOT NULL,
    improvement_percentage jsonb DEFAULT '{}'::jsonb,
    parameters jsonb DEFAULT '{}'::jsonb,
    is_applied boolean DEFAULT false,
    is_active boolean DEFAULT true,
    metadata jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.conversation_optimizations OWNER TO openclaw;

--
-- Name: conversation_optimizations_id_seq; Type: SEQUENCE; Schema: public; Owner: openclaw
--

CREATE SEQUENCE public.conversation_optimizations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.conversation_optimizations_id_seq OWNER TO openclaw;

--
-- Name: conversation_optimizations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: openclaw
--

ALTER SEQUENCE public.conversation_optimizations_id_seq OWNED BY public.conversation_optimizations.id;


--
-- Name: conversations; Type: TABLE; Schema: public; Owner: openclaw
--

CREATE TABLE public.conversations (
    id integer NOT NULL,
    conversation_id character varying(100) NOT NULL,
    channel character varying(50) NOT NULL,
    user_id character varying(100),
    title text,
    status character varying(20) DEFAULT 'active'::character varying,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE public.conversations OWNER TO openclaw;

--
-- Name: TABLE conversations; Type: COMMENT; Schema: public; Owner: openclaw
--

COMMENT ON TABLE public.conversations IS 'OpenClaw 對話會話';


--
-- Name: conversations_id_seq; Type: SEQUENCE; Schema: public; Owner: openclaw
--

CREATE SEQUENCE public.conversations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.conversations_id_seq OWNER TO openclaw;

--
-- Name: conversations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: openclaw
--

ALTER SEQUENCE public.conversations_id_seq OWNED BY public.conversations.id;


--
-- Name: knowledge_base; Type: TABLE; Schema: public; Owner: openclaw
--

CREATE TABLE public.knowledge_base (
    id integer NOT NULL,
    entry_id character varying(100) NOT NULL,
    category character varying(50) NOT NULL,
    title character varying(255) NOT NULL,
    content text NOT NULL,
    summary text,
    tags text[],
    conversation_state character varying(50) DEFAULT 'new_conversation'::character varying,
    confidence double precision DEFAULT 0.0,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    source character varying(50) DEFAULT 'neur-opt'::character varying,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE public.knowledge_base OWNER TO openclaw;

--
-- Name: TABLE knowledge_base; Type: COMMENT; Schema: public; Owner: openclaw
--

COMMENT ON TABLE public.knowledge_base IS 'OpenClaw 知識庫';


--
-- Name: knowledge_base_id_seq; Type: SEQUENCE; Schema: public; Owner: openclaw
--

CREATE SEQUENCE public.knowledge_base_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.knowledge_base_id_seq OWNER TO openclaw;

--
-- Name: knowledge_base_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: openclaw
--

ALTER SEQUENCE public.knowledge_base_id_seq OWNED BY public.knowledge_base.id;


--
-- Name: logs; Type: TABLE; Schema: public; Owner: openclaw
--

CREATE TABLE public.logs (
    id integer NOT NULL,
    log_id character varying(100) NOT NULL,
    level character varying(20) NOT NULL,
    category character varying(50),
    message text NOT NULL,
    agent_id character varying(50),
    context jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE public.logs OWNER TO openclaw;

--
-- Name: TABLE logs; Type: COMMENT; Schema: public; Owner: openclaw
--

COMMENT ON TABLE public.logs IS 'OpenClaw 系統日誌';


--
-- Name: logs_id_seq; Type: SEQUENCE; Schema: public; Owner: openclaw
--

CREATE SEQUENCE public.logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.logs_id_seq OWNER TO openclaw;

--
-- Name: logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: openclaw
--

ALTER SEQUENCE public.logs_id_seq OWNED BY public.logs.id;


--
-- Name: memory; Type: TABLE; Schema: public; Owner: openclaw
--

CREATE TABLE public.memory (
    id integer NOT NULL,
    memory_id character varying(100) NOT NULL,
    title character varying(255) NOT NULL,
    content text NOT NULL,
    category character varying(50),
    importance integer DEFAULT 3,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    access_count integer DEFAULT 0,
    last_accessed_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE public.memory OWNER TO openclaw;

--
-- Name: TABLE memory; Type: COMMENT; Schema: public; Owner: openclaw
--

COMMENT ON TABLE public.memory IS 'OpenClaw 長期記憶';


--
-- Name: memory_id_seq; Type: SEQUENCE; Schema: public; Owner: openclaw
--

CREATE SEQUENCE public.memory_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.memory_id_seq OWNER TO openclaw;

--
-- Name: memory_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: openclaw
--

ALTER SEQUENCE public.memory_id_seq OWNED BY public.memory.id;


--
-- Name: messages; Type: TABLE; Schema: public; Owner: openclaw
--

CREATE TABLE public.messages (
    id integer NOT NULL,
    message_id character varying(100) NOT NULL,
    conversation_id character varying(100) NOT NULL,
    role character varying(20) NOT NULL,
    content text NOT NULL,
    agent_id character varying(50),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    token_count integer DEFAULT 0,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE public.messages OWNER TO openclaw;

--
-- Name: TABLE messages; Type: COMMENT; Schema: public; Owner: openclaw
--

COMMENT ON TABLE public.messages IS 'OpenClaw 對話消息';


--
-- Name: messages_id_seq; Type: SEQUENCE; Schema: public; Owner: openclaw
--

CREATE SEQUENCE public.messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.messages_id_seq OWNER TO openclaw;

--
-- Name: messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: openclaw
--

ALTER SEQUENCE public.messages_id_seq OWNED BY public.messages.id;


--
-- Name: session_state; Type: TABLE; Schema: public; Owner: openclaw
--

CREATE TABLE public.session_state (
    id integer NOT NULL,
    session_id character varying(100) NOT NULL,
    conversation_id character varying(100),
    current_agent_id character varying(50),
    state jsonb DEFAULT '{}'::jsonb NOT NULL,
    context_window integer[],
    metadata jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    last_message_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.session_state OWNER TO openclaw;

--
-- Name: TABLE session_state; Type: COMMENT; Schema: public; Owner: openclaw
--

COMMENT ON TABLE public.session_state IS 'OpenClaw 對話狀態';


--
-- Name: session_state_id_seq; Type: SEQUENCE; Schema: public; Owner: openclaw
--

CREATE SEQUENCE public.session_state_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.session_state_id_seq OWNER TO openclaw;

--
-- Name: session_state_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: openclaw
--

ALTER SEQUENCE public.session_state_id_seq OWNED BY public.session_state.id;


--
-- Name: short_term_memory; Type: TABLE; Schema: public; Owner: openclaw
--

CREATE TABLE public.short_term_memory (
    id integer NOT NULL,
    conversation_id character varying(100) NOT NULL,
    session_id character varying(100),
    user_id character varying(100) NOT NULL,
    message_content text NOT NULL,
    message_metadata jsonb DEFAULT '{}'::jsonb,
    "timestamp" timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.short_term_memory OWNER TO openclaw;

--
-- Name: short_term_memory_id_seq; Type: SEQUENCE; Schema: public; Owner: openclaw
--

CREATE SEQUENCE public.short_term_memory_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.short_term_memory_id_seq OWNER TO openclaw;

--
-- Name: short_term_memory_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: openclaw
--

ALTER SEQUENCE public.short_term_memory_id_seq OWNED BY public.short_term_memory.id;


--
-- Name: system_metrics; Type: TABLE; Schema: public; Owner: openclaw
--

CREATE TABLE public.system_metrics (
    id integer NOT NULL,
    metric_id character varying(100) NOT NULL,
    metric_name character varying(100) NOT NULL,
    metric_value double precision,
    metric_type character varying(50),
    agent_id character varying(50),
    "timestamp" timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE public.system_metrics OWNER TO openclaw;

--
-- Name: TABLE system_metrics; Type: COMMENT; Schema: public; Owner: openclaw
--

COMMENT ON TABLE public.system_metrics IS 'OpenClaw 系統指標';


--
-- Name: system_metrics_id_seq; Type: SEQUENCE; Schema: public; Owner: openclaw
--

CREATE SEQUENCE public.system_metrics_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.system_metrics_id_seq OWNER TO openclaw;

--
-- Name: system_metrics_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: openclaw
--

ALTER SEQUENCE public.system_metrics_id_seq OWNED BY public.system_metrics.id;


--
-- Name: system_state; Type: TABLE; Schema: public; Owner: openclaw
--

CREATE TABLE public.system_state (
    id integer NOT NULL,
    state_key character varying(100) NOT NULL,
    state_value jsonb NOT NULL,
    state_type character varying(50) DEFAULT 'configuration'::character varying,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.system_state OWNER TO openclaw;

--
-- Name: system_state_id_seq; Type: SEQUENCE; Schema: public; Owner: openclaw
--

CREATE SEQUENCE public.system_state_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.system_state_id_seq OWNER TO openclaw;

--
-- Name: system_state_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: openclaw
--

ALTER SEQUENCE public.system_state_id_seq OWNED BY public.system_state.id;


--
-- Name: tasks; Type: TABLE; Schema: public; Owner: openclaw
--

CREATE TABLE public.tasks (
    id integer NOT NULL,
    task_id character varying(100) NOT NULL,
    title character varying(255) NOT NULL,
    description text,
    status character varying(20) DEFAULT 'pending'::character varying,
    priority integer DEFAULT 3,
    assigned_agent_id character varying(50),
    conversation_id character varying(100),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    due_at timestamp without time zone,
    completed_at timestamp without time zone,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE public.tasks OWNER TO openclaw;

--
-- Name: TABLE tasks; Type: COMMENT; Schema: public; Owner: openclaw
--

COMMENT ON TABLE public.tasks IS 'OpenClaw 任務列表';


--
-- Name: tasks_id_seq; Type: SEQUENCE; Schema: public; Owner: openclaw
--

CREATE SEQUENCE public.tasks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tasks_id_seq OWNER TO openclaw;

--
-- Name: tasks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: openclaw
--

ALTER SEQUENCE public.tasks_id_seq OWNED BY public.tasks.id;


--
-- Name: user_actions; Type: TABLE; Schema: public; Owner: openclaw
--

CREATE TABLE public.user_actions (
    id integer NOT NULL,
    action_id character varying(100) NOT NULL,
    user_id character varying(100),
    action_type character varying(50) NOT NULL,
    target_type character varying(50),
    target_id character varying(100),
    description text,
    status character varying(20) DEFAULT 'completed'::character varying,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE public.user_actions OWNER TO openclaw;

--
-- Name: TABLE user_actions; Type: COMMENT; Schema: public; Owner: openclaw
--

COMMENT ON TABLE public.user_actions IS 'OpenClaw 用戶操作記錄';


--
-- Name: user_actions_id_seq; Type: SEQUENCE; Schema: public; Owner: openclaw
--

CREATE SEQUENCE public.user_actions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_actions_id_seq OWNER TO openclaw;

--
-- Name: user_actions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: openclaw
--

ALTER SEQUENCE public.user_actions_id_seq OWNED BY public.user_actions.id;


--
-- Name: user_preferences; Type: TABLE; Schema: public; Owner: openclaw
--

CREATE TABLE public.user_preferences (
    id integer NOT NULL,
    user_id character varying(100) NOT NULL,
    preference_key character varying(100) NOT NULL,
    preference_value jsonb NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.user_preferences OWNER TO openclaw;

--
-- Name: user_preferences_id_seq; Type: SEQUENCE; Schema: public; Owner: openclaw
--

CREATE SEQUENCE public.user_preferences_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_preferences_id_seq OWNER TO openclaw;

--
-- Name: user_preferences_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: openclaw
--

ALTER SEQUENCE public.user_preferences_id_seq OWNED BY public.user_preferences.id;


--
-- Name: weather_alerts; Type: TABLE; Schema: public; Owner: openclaw
--

CREATE TABLE public.weather_alerts (
    id integer NOT NULL,
    alert_id character varying(100),
    alert_type character varying(50),
    severity character varying(20),
    title text,
    description text,
    effect_start_time timestamp with time zone,
    effect_end_time timestamp with time zone,
    location character varying(100) DEFAULT 'HKO'::character varying,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    sent_at timestamp with time zone,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE public.weather_alerts OWNER TO openclaw;

--
-- Name: weather_alerts_id_seq; Type: SEQUENCE; Schema: public; Owner: openclaw
--

CREATE SEQUENCE public.weather_alerts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.weather_alerts_id_seq OWNER TO openclaw;

--
-- Name: weather_alerts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: openclaw
--

ALTER SEQUENCE public.weather_alerts_id_seq OWNED BY public.weather_alerts.id;


--
-- Name: weather_data; Type: TABLE; Schema: public; Owner: openclaw
--

CREATE TABLE public.weather_data (
    id integer NOT NULL,
    data_id character varying(100),
    observation_time timestamp with time zone NOT NULL,
    temperature double precision,
    humidity double precision,
    rainfall double precision,
    wind_speed double precision,
    wind_direction character varying(10),
    weather_condition character varying(50),
    location character varying(100) DEFAULT 'HKO'::character varying,
    source character varying(50) DEFAULT 'HKO'::character varying,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE public.weather_data OWNER TO openclaw;

--
-- Name: weather_data_id_seq; Type: SEQUENCE; Schema: public; Owner: openclaw
--

CREATE SEQUENCE public.weather_data_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.weather_data_id_seq OWNER TO openclaw;

--
-- Name: weather_data_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: openclaw
--

ALTER SEQUENCE public.weather_data_id_seq OWNED BY public.weather_data.id;


--
-- Name: weather_forecast; Type: TABLE; Schema: public; Owner: openclaw
--

CREATE TABLE public.weather_forecast (
    id integer NOT NULL,
    forecast_id character varying(100),
    forecast_time timestamp with time zone NOT NULL,
    temperature_min double precision,
    temperature_max double precision,
    weather_condition character varying(50),
    humidity double precision,
    rainfall_probability double precision,
    location character varying(100) DEFAULT 'HKO'::character varying,
    source character varying(50) DEFAULT 'HKO'::character varying,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE public.weather_forecast OWNER TO openclaw;

--
-- Name: weather_forecast_id_seq; Type: SEQUENCE; Schema: public; Owner: openclaw
--

CREATE SEQUENCE public.weather_forecast_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.weather_forecast_id_seq OWNER TO openclaw;

--
-- Name: weather_forecast_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: openclaw
--

ALTER SEQUENCE public.weather_forecast_id_seq OWNED BY public.weather_forecast.id;


--
-- Name: weather_settings; Type: TABLE; Schema: public; Owner: openclaw
--

CREATE TABLE public.weather_settings (
    id integer NOT NULL,
    setting_id character varying(100),
    setting_key character varying(50) NOT NULL,
    setting_value text NOT NULL,
    setting_type character varying(20) DEFAULT 'string'::character varying,
    description text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    metadata jsonb DEFAULT '{}'::jsonb
);


ALTER TABLE public.weather_settings OWNER TO openclaw;

--
-- Name: weather_settings_id_seq; Type: SEQUENCE; Schema: public; Owner: openclaw
--

CREATE SEQUENCE public.weather_settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.weather_settings_id_seq OWNER TO openclaw;

--
-- Name: weather_settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: openclaw
--

ALTER SEQUENCE public.weather_settings_id_seq OWNED BY public.weather_settings.id;


--
-- Name: agents id; Type: DEFAULT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.agents ALTER COLUMN id SET DEFAULT nextval('public.agents_id_seq'::regclass);


--
-- Name: conversation_optimizations id; Type: DEFAULT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.conversation_optimizations ALTER COLUMN id SET DEFAULT nextval('public.conversation_optimizations_id_seq'::regclass);


--
-- Name: conversations id; Type: DEFAULT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.conversations ALTER COLUMN id SET DEFAULT nextval('public.conversations_id_seq'::regclass);


--
-- Name: knowledge_base id; Type: DEFAULT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.knowledge_base ALTER COLUMN id SET DEFAULT nextval('public.knowledge_base_id_seq'::regclass);


--
-- Name: logs id; Type: DEFAULT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.logs ALTER COLUMN id SET DEFAULT nextval('public.logs_id_seq'::regclass);


--
-- Name: memory id; Type: DEFAULT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.memory ALTER COLUMN id SET DEFAULT nextval('public.memory_id_seq'::regclass);


--
-- Name: messages id; Type: DEFAULT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.messages ALTER COLUMN id SET DEFAULT nextval('public.messages_id_seq'::regclass);


--
-- Name: session_state id; Type: DEFAULT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.session_state ALTER COLUMN id SET DEFAULT nextval('public.session_state_id_seq'::regclass);


--
-- Name: short_term_memory id; Type: DEFAULT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.short_term_memory ALTER COLUMN id SET DEFAULT nextval('public.short_term_memory_id_seq'::regclass);


--
-- Name: system_metrics id; Type: DEFAULT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.system_metrics ALTER COLUMN id SET DEFAULT nextval('public.system_metrics_id_seq'::regclass);


--
-- Name: system_state id; Type: DEFAULT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.system_state ALTER COLUMN id SET DEFAULT nextval('public.system_state_id_seq'::regclass);


--
-- Name: tasks id; Type: DEFAULT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.tasks ALTER COLUMN id SET DEFAULT nextval('public.tasks_id_seq'::regclass);


--
-- Name: user_actions id; Type: DEFAULT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.user_actions ALTER COLUMN id SET DEFAULT nextval('public.user_actions_id_seq'::regclass);


--
-- Name: user_preferences id; Type: DEFAULT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.user_preferences ALTER COLUMN id SET DEFAULT nextval('public.user_preferences_id_seq'::regclass);


--
-- Name: weather_alerts id; Type: DEFAULT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.weather_alerts ALTER COLUMN id SET DEFAULT nextval('public.weather_alerts_id_seq'::regclass);


--
-- Name: weather_data id; Type: DEFAULT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.weather_data ALTER COLUMN id SET DEFAULT nextval('public.weather_data_id_seq'::regclass);


--
-- Name: weather_forecast id; Type: DEFAULT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.weather_forecast ALTER COLUMN id SET DEFAULT nextval('public.weather_forecast_id_seq'::regclass);


--
-- Name: weather_settings id; Type: DEFAULT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.weather_settings ALTER COLUMN id SET DEFAULT nextval('public.weather_settings_id_seq'::regclass);


--
-- Data for Name: agents; Type: TABLE DATA; Schema: public; Owner: openclaw
--

COPY public.agents (id, agent_id, name, model, provider, workspace, created_at, updated_at, is_active, metadata) FROM stdin;
1	main	Main Agent	zai/glm-4.7	zai	~/.openclaw/workspace	2026-02-26 08:21:11.586049+08	2026-02-26 08:21:11.586049+08	t	{"role": "orchestrator", "type": "main"}
2	classifier	Classifier	ollama/qwen2.5:1.5b	ollama	~/.openclaw/workspace-classifier	2026-02-26 08:21:11.586049+08	2026-02-26 08:21:11.586049+08	t	{"role": "classifier", "type": "local"}
3	chat	Chat Agent	zai/glm-4.7-flashx	zai	~/.openclaw/workspace-chat	2026-02-26 08:21:11.586049+08	2026-02-26 08:21:11.586049+08	t	{"role": "chat", "type": "cloud"}
4	task	Task Agent	zai/glm-4.7-flash	zai	~/.openclaw/workspace-task	2026-02-26 08:21:11.586049+08	2026-02-26 08:21:11.586049+08	t	{"role": "task", "type": "cloud"}
5	coding	Coding Agent	zai/glm-4.7	zai	~/.openclaw/workspace-coding	2026-02-26 08:21:11.586049+08	2026-02-26 08:21:11.586049+08	t	{"role": "coding", "type": "cloud"}
6	data	Data Agent	zai/glm-4.7-flash	zai	~/.openclaw/workspace-data	2026-02-26 08:21:11.586049+08	2026-02-26 08:21:11.586049+08	t	{"role": "data", "type": "cloud"}
7	qa	QA Agent	zai/glm-4.7-flash	zai	~/.openclaw/workspace-qa	2026-02-26 08:21:11.586049+08	2026-02-26 08:21:11.586049+08	t	{"role": "qa", "type": "cloud"}
\.


--
-- Data for Name: conversation_optimizations; Type: TABLE DATA; Schema: public; Owner: openclaw
--

COPY public.conversation_optimizations (id, optimization_id, conversation_id, optimization_type, optimization_date, before_metrics, after_metrics, improvement_percentage, parameters, is_applied, is_active, metadata, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: conversations; Type: TABLE DATA; Schema: public; Owner: openclaw
--

COPY public.conversations (id, conversation_id, channel, user_id, title, status, created_at, updated_at, metadata) FROM stdin;
1	test_conv_001	telegram	test_user	測試對話	active	2026-02-26 08:23:59.304428+08	2026-02-26 08:23:59.304428+08	{}
2	test_integration_conv	telegram	jarvis	數據庫集成測試	active	2026-02-26 08:28:02.942319+08	2026-02-26 08:28:02.942319+08	{}
\.


--
-- Data for Name: knowledge_base; Type: TABLE DATA; Schema: public; Owner: openclaw
--

COPY public.knowledge_base (id, entry_id, category, title, content, summary, tags, conversation_state, confidence, created_at, updated_at, source, metadata) FROM stdin;
1	test_kb_001	CODE	測試知識	這是測試知識內容	測試摘要	{python,test}	new_conversation	0	2026-02-26 08:23:59.368967+08	2026-02-26 08:23:59.368967+08	neur-opt	{}
2	test_integration_kb_001	CODE	Python 數據庫集成	如何使用 PostgreSQL 數據庫進行數據存儲	完整數據庫集成指南	{python,postgresql,database,integration}	new_conversation	0	2026-02-26 08:28:03.00376+08	2026-02-26 08:28:03.00376+08	neur-opt	{}
\.


--
-- Data for Name: logs; Type: TABLE DATA; Schema: public; Owner: openclaw
--

COPY public.logs (id, log_id, level, category, message, agent_id, context, created_at, metadata) FROM stdin;
1	test_log_1772065439	INFO	database	測試日誌消息	main	{}	2026-02-26 08:23:59.431244+08	{}
2	test_log_1772065683	INFO	database	數據庫集成測試完成	main	{}	2026-02-26 08:28:03.097409+08	{}
\.


--
-- Data for Name: memory; Type: TABLE DATA; Schema: public; Owner: openclaw
--

COPY public.memory (id, memory_id, title, content, category, importance, is_active, created_at, updated_at, access_count, last_accessed_at, metadata) FROM stdin;
1	test_mem_001	測試記憶	這是測試記憶內容	preference	5	t	2026-02-26 08:23:59.400655+08	2026-02-26 08:23:59.400655+08	0	2026-02-26 08:23:59.400655+08	{}
2	test_integration_mem_001	數據庫集成偏好	用戶喜歡使用 PostgreSQL 進行數據持久化	preference	5	t	2026-02-26 08:28:03.034031+08	2026-02-26 08:28:03.034031+08	0	2026-02-26 08:28:03.034031+08	{}
\.


--
-- Data for Name: messages; Type: TABLE DATA; Schema: public; Owner: openclaw
--

COPY public.messages (id, message_id, conversation_id, role, content, agent_id, created_at, token_count, metadata) FROM stdin;
1	test_msg_001	test_conv_001	user	這是測試消息	chat	2026-02-26 08:23:59.335738+08	50	{}
2	test_integration_msg_001	test_integration_conv	user	測試數據庫集成功能	main	2026-02-26 08:28:02.971185+08	100	{}
\.


--
-- Data for Name: session_state; Type: TABLE DATA; Schema: public; Owner: openclaw
--

COPY public.session_state (id, session_id, conversation_id, current_agent_id, state, context_window, metadata, created_at, updated_at, last_message_at) FROM stdin;
\.


--
-- Data for Name: short_term_memory; Type: TABLE DATA; Schema: public; Owner: openclaw
--

COPY public.short_term_memory (id, conversation_id, session_id, user_id, message_content, message_metadata, "timestamp", created_at) FROM stdin;
\.


--
-- Data for Name: system_metrics; Type: TABLE DATA; Schema: public; Owner: openclaw
--

COPY public.system_metrics (id, metric_id, metric_name, metric_value, metric_type, agent_id, "timestamp", metadata) FROM stdin;
1	test_metric_1772065439	response_time	1.234	performance	chat	2026-02-26 08:23:59.495429+08	{}
2	test_metric_1772065683	database_operations	42	performance	main	2026-02-26 08:28:03.12839+08	{}
\.


--
-- Data for Name: system_state; Type: TABLE DATA; Schema: public; Owner: openclaw
--

COPY public.system_state (id, state_key, state_value, state_type, updated_at) FROM stdin;
\.


--
-- Data for Name: tasks; Type: TABLE DATA; Schema: public; Owner: openclaw
--

COPY public.tasks (id, task_id, title, description, status, priority, assigned_agent_id, conversation_id, created_at, updated_at, due_at, completed_at, metadata) FROM stdin;
1	test_task_001	測試任務	這是測試任務描述	pending	1	coding	\N	2026-02-26 08:23:59.463162+08	2026-02-26 08:23:59.463162+08	\N	\N	{}
2	test_integration_task_001	測試數據庫讀寫	測試數據庫的讀寫性能和可靠性	pending	1	coding	\N	2026-02-26 08:28:03.06441+08	2026-02-26 08:28:03.06441+08	\N	\N	{}
\.


--
-- Data for Name: user_actions; Type: TABLE DATA; Schema: public; Owner: openclaw
--

COPY public.user_actions (id, action_id, user_id, action_type, target_type, target_id, description, status, created_at, metadata) FROM stdin;
\.


--
-- Data for Name: user_preferences; Type: TABLE DATA; Schema: public; Owner: openclaw
--

COPY public.user_preferences (id, user_id, preference_key, preference_value, updated_at) FROM stdin;
\.


--
-- Data for Name: weather_alerts; Type: TABLE DATA; Schema: public; Owner: openclaw
--

COPY public.weather_alerts (id, alert_id, alert_type, severity, title, description, effect_start_time, effect_end_time, location, is_active, created_at, updated_at, sent_at, metadata) FROM stdin;
\.


--
-- Data for Name: weather_data; Type: TABLE DATA; Schema: public; Owner: openclaw
--

COPY public.weather_data (id, data_id, observation_time, temperature, humidity, rainfall, wind_speed, wind_direction, weather_condition, location, source, created_at, updated_at, metadata) FROM stdin;
\.


--
-- Data for Name: weather_forecast; Type: TABLE DATA; Schema: public; Owner: openclaw
--

COPY public.weather_forecast (id, forecast_id, forecast_time, temperature_min, temperature_max, weather_condition, humidity, rainfall_probability, location, source, created_at, metadata) FROM stdin;
\.


--
-- Data for Name: weather_settings; Type: TABLE DATA; Schema: public; Owner: openclaw
--

COPY public.weather_settings (id, setting_id, setting_key, setting_value, setting_type, description, created_at, updated_at, metadata) FROM stdin;
\.


--
-- Name: agents_id_seq; Type: SEQUENCE SET; Schema: public; Owner: openclaw
--

SELECT pg_catalog.setval('public.agents_id_seq', 7, true);


--
-- Name: conversation_optimizations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: openclaw
--

SELECT pg_catalog.setval('public.conversation_optimizations_id_seq', 1, false);


--
-- Name: conversations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: openclaw
--

SELECT pg_catalog.setval('public.conversations_id_seq', 2, true);


--
-- Name: knowledge_base_id_seq; Type: SEQUENCE SET; Schema: public; Owner: openclaw
--

SELECT pg_catalog.setval('public.knowledge_base_id_seq', 2, true);


--
-- Name: logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: openclaw
--

SELECT pg_catalog.setval('public.logs_id_seq', 3, true);


--
-- Name: memory_id_seq; Type: SEQUENCE SET; Schema: public; Owner: openclaw
--

SELECT pg_catalog.setval('public.memory_id_seq', 2, true);


--
-- Name: messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: openclaw
--

SELECT pg_catalog.setval('public.messages_id_seq', 2, true);


--
-- Name: session_state_id_seq; Type: SEQUENCE SET; Schema: public; Owner: openclaw
--

SELECT pg_catalog.setval('public.session_state_id_seq', 1, false);


--
-- Name: short_term_memory_id_seq; Type: SEQUENCE SET; Schema: public; Owner: openclaw
--

SELECT pg_catalog.setval('public.short_term_memory_id_seq', 1, false);


--
-- Name: system_metrics_id_seq; Type: SEQUENCE SET; Schema: public; Owner: openclaw
--

SELECT pg_catalog.setval('public.system_metrics_id_seq', 2, true);


--
-- Name: system_state_id_seq; Type: SEQUENCE SET; Schema: public; Owner: openclaw
--

SELECT pg_catalog.setval('public.system_state_id_seq', 1, false);


--
-- Name: tasks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: openclaw
--

SELECT pg_catalog.setval('public.tasks_id_seq', 2, true);


--
-- Name: user_actions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: openclaw
--

SELECT pg_catalog.setval('public.user_actions_id_seq', 1, false);


--
-- Name: user_preferences_id_seq; Type: SEQUENCE SET; Schema: public; Owner: openclaw
--

SELECT pg_catalog.setval('public.user_preferences_id_seq', 1, false);


--
-- Name: weather_alerts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: openclaw
--

SELECT pg_catalog.setval('public.weather_alerts_id_seq', 1, false);


--
-- Name: weather_data_id_seq; Type: SEQUENCE SET; Schema: public; Owner: openclaw
--

SELECT pg_catalog.setval('public.weather_data_id_seq', 1, false);


--
-- Name: weather_forecast_id_seq; Type: SEQUENCE SET; Schema: public; Owner: openclaw
--

SELECT pg_catalog.setval('public.weather_forecast_id_seq', 1, false);


--
-- Name: weather_settings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: openclaw
--

SELECT pg_catalog.setval('public.weather_settings_id_seq', 1, false);


--
-- Name: agents agents_agent_id_key; Type: CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.agents
    ADD CONSTRAINT agents_agent_id_key UNIQUE (agent_id);


--
-- Name: agents agents_pkey; Type: CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.agents
    ADD CONSTRAINT agents_pkey PRIMARY KEY (id);


--
-- Name: conversation_optimizations conversation_optimizations_optimization_id_key; Type: CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.conversation_optimizations
    ADD CONSTRAINT conversation_optimizations_optimization_id_key UNIQUE (optimization_id);


--
-- Name: conversation_optimizations conversation_optimizations_pkey; Type: CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.conversation_optimizations
    ADD CONSTRAINT conversation_optimizations_pkey PRIMARY KEY (id);


--
-- Name: conversations conversations_conversation_id_key; Type: CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.conversations
    ADD CONSTRAINT conversations_conversation_id_key UNIQUE (conversation_id);


--
-- Name: conversations conversations_pkey; Type: CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.conversations
    ADD CONSTRAINT conversations_pkey PRIMARY KEY (id);


--
-- Name: knowledge_base knowledge_base_entry_id_key; Type: CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.knowledge_base
    ADD CONSTRAINT knowledge_base_entry_id_key UNIQUE (entry_id);


--
-- Name: knowledge_base knowledge_base_pkey; Type: CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.knowledge_base
    ADD CONSTRAINT knowledge_base_pkey PRIMARY KEY (id);


--
-- Name: logs logs_log_id_key; Type: CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.logs
    ADD CONSTRAINT logs_log_id_key UNIQUE (log_id);


--
-- Name: logs logs_pkey; Type: CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.logs
    ADD CONSTRAINT logs_pkey PRIMARY KEY (id);


--
-- Name: memory memory_memory_id_key; Type: CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.memory
    ADD CONSTRAINT memory_memory_id_key UNIQUE (memory_id);


--
-- Name: memory memory_pkey; Type: CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.memory
    ADD CONSTRAINT memory_pkey PRIMARY KEY (id);


--
-- Name: messages messages_message_id_key; Type: CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_message_id_key UNIQUE (message_id);


--
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);


--
-- Name: session_state session_state_pkey; Type: CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.session_state
    ADD CONSTRAINT session_state_pkey PRIMARY KEY (id);


--
-- Name: session_state session_state_session_id_key; Type: CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.session_state
    ADD CONSTRAINT session_state_session_id_key UNIQUE (session_id);


--
-- Name: short_term_memory short_term_memory_pkey; Type: CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.short_term_memory
    ADD CONSTRAINT short_term_memory_pkey PRIMARY KEY (id);


--
-- Name: system_metrics system_metrics_metric_id_key; Type: CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.system_metrics
    ADD CONSTRAINT system_metrics_metric_id_key UNIQUE (metric_id);


--
-- Name: system_metrics system_metrics_pkey; Type: CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.system_metrics
    ADD CONSTRAINT system_metrics_pkey PRIMARY KEY (id);


--
-- Name: system_state system_state_pkey; Type: CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.system_state
    ADD CONSTRAINT system_state_pkey PRIMARY KEY (id);


--
-- Name: system_state system_state_state_key_key; Type: CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.system_state
    ADD CONSTRAINT system_state_state_key_key UNIQUE (state_key);


--
-- Name: tasks tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (id);


--
-- Name: tasks tasks_task_id_key; Type: CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_task_id_key UNIQUE (task_id);


--
-- Name: user_actions user_actions_action_id_key; Type: CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.user_actions
    ADD CONSTRAINT user_actions_action_id_key UNIQUE (action_id);


--
-- Name: user_actions user_actions_pkey; Type: CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.user_actions
    ADD CONSTRAINT user_actions_pkey PRIMARY KEY (id);


--
-- Name: user_preferences user_preferences_pkey; Type: CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.user_preferences
    ADD CONSTRAINT user_preferences_pkey PRIMARY KEY (id);


--
-- Name: user_preferences user_preferences_user_id_preference_key_key; Type: CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.user_preferences
    ADD CONSTRAINT user_preferences_user_id_preference_key_key UNIQUE (user_id, preference_key);


--
-- Name: weather_alerts weather_alerts_alert_id_key; Type: CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.weather_alerts
    ADD CONSTRAINT weather_alerts_alert_id_key UNIQUE (alert_id);


--
-- Name: weather_alerts weather_alerts_pkey; Type: CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.weather_alerts
    ADD CONSTRAINT weather_alerts_pkey PRIMARY KEY (id);


--
-- Name: weather_data weather_data_data_id_key; Type: CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.weather_data
    ADD CONSTRAINT weather_data_data_id_key UNIQUE (data_id);


--
-- Name: weather_data weather_data_pkey; Type: CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.weather_data
    ADD CONSTRAINT weather_data_pkey PRIMARY KEY (id);


--
-- Name: weather_forecast weather_forecast_forecast_id_key; Type: CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.weather_forecast
    ADD CONSTRAINT weather_forecast_forecast_id_key UNIQUE (forecast_id);


--
-- Name: weather_forecast weather_forecast_pkey; Type: CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.weather_forecast
    ADD CONSTRAINT weather_forecast_pkey PRIMARY KEY (id);


--
-- Name: weather_settings weather_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.weather_settings
    ADD CONSTRAINT weather_settings_pkey PRIMARY KEY (id);


--
-- Name: weather_settings weather_settings_setting_id_key; Type: CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.weather_settings
    ADD CONSTRAINT weather_settings_setting_id_key UNIQUE (setting_id);


--
-- Name: idx_conversation_optimizations_active; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_conversation_optimizations_active ON public.conversation_optimizations USING btree (is_active, is_applied);


--
-- Name: idx_conversation_optimizations_type; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_conversation_optimizations_type ON public.conversation_optimizations USING btree (optimization_type, optimization_date DESC);


--
-- Name: idx_conversations_channel; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_conversations_channel ON public.conversations USING btree (channel);


--
-- Name: idx_conversations_created_at; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_conversations_created_at ON public.conversations USING btree (created_at DESC);


--
-- Name: idx_conversations_status; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_conversations_status ON public.conversations USING btree (status);


--
-- Name: idx_conversations_user; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_conversations_user ON public.conversations USING btree (user_id);


--
-- Name: idx_conversations_user_id; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_conversations_user_id ON public.conversations USING btree (user_id);


--
-- Name: idx_kb_category; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_kb_category ON public.knowledge_base USING btree (category);


--
-- Name: idx_kb_conversation_state; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_kb_conversation_state ON public.knowledge_base USING btree (conversation_state);


--
-- Name: idx_kb_created_at; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_kb_created_at ON public.knowledge_base USING btree (created_at DESC);


--
-- Name: idx_kb_tags; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_kb_tags ON public.knowledge_base USING gin (tags);


--
-- Name: idx_logs_agent_id; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_logs_agent_id ON public.logs USING btree (agent_id);


--
-- Name: idx_logs_category; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_logs_category ON public.logs USING btree (category);


--
-- Name: idx_logs_created_at; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_logs_created_at ON public.logs USING btree (created_at DESC);


--
-- Name: idx_logs_level; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_logs_level ON public.logs USING btree (level);


--
-- Name: idx_memory_category; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_memory_category ON public.memory USING btree (category);


--
-- Name: idx_memory_created_at; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_memory_created_at ON public.memory USING btree (created_at DESC);


--
-- Name: idx_memory_importance; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_memory_importance ON public.memory USING btree (importance DESC);


--
-- Name: idx_memory_is_active; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_memory_is_active ON public.memory USING btree (is_active);


--
-- Name: idx_messages_agent_id; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_messages_agent_id ON public.messages USING btree (agent_id);


--
-- Name: idx_messages_conversation_id; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_messages_conversation_id ON public.messages USING btree (conversation_id);


--
-- Name: idx_messages_created_at; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_messages_created_at ON public.messages USING btree (created_at DESC);


--
-- Name: idx_session_state_conversation_id; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_session_state_conversation_id ON public.session_state USING btree (conversation_id);


--
-- Name: idx_session_state_current_agent; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_session_state_current_agent ON public.session_state USING btree (current_agent_id);


--
-- Name: idx_session_state_session_id; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_session_state_session_id ON public.session_state USING btree (session_id);


--
-- Name: idx_short_term_conversation; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_short_term_conversation ON public.short_term_memory USING btree (conversation_id, "timestamp" DESC);


--
-- Name: idx_short_term_session; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_short_term_session ON public.short_term_memory USING btree (session_id, "timestamp" DESC);


--
-- Name: idx_system_metrics_name; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_system_metrics_name ON public.system_metrics USING btree (metric_name);


--
-- Name: idx_system_metrics_timestamp; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_system_metrics_timestamp ON public.system_metrics USING btree ("timestamp" DESC);


--
-- Name: idx_system_state; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_system_state ON public.system_state USING btree (state_key, updated_at DESC);


--
-- Name: idx_tasks_assigned_agent; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_tasks_assigned_agent ON public.tasks USING btree (assigned_agent_id);


--
-- Name: idx_tasks_due_at; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_tasks_due_at ON public.tasks USING btree (due_at);


--
-- Name: idx_tasks_priority; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_tasks_priority ON public.tasks USING btree (priority DESC);


--
-- Name: idx_tasks_status; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_tasks_status ON public.tasks USING btree (status);


--
-- Name: idx_user_actions_action_type; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_user_actions_action_type ON public.user_actions USING btree (action_type);


--
-- Name: idx_user_actions_created_at; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_user_actions_created_at ON public.user_actions USING btree (created_at DESC);


--
-- Name: idx_user_actions_target_id; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_user_actions_target_id ON public.user_actions USING btree (target_id);


--
-- Name: idx_user_actions_user_id; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_user_actions_user_id ON public.user_actions USING btree (user_id);


--
-- Name: idx_user_preferences; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_user_preferences ON public.user_preferences USING btree (user_id);


--
-- Name: idx_weather_alerts_active; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_weather_alerts_active ON public.weather_alerts USING btree (is_active, severity);


--
-- Name: idx_weather_alerts_time; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_weather_alerts_time ON public.weather_alerts USING btree (effect_start_time DESC);


--
-- Name: idx_weather_alerts_type; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_weather_alerts_type ON public.weather_alerts USING btree (alert_type);


--
-- Name: idx_weather_data_location; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_weather_data_location ON public.weather_data USING btree (location);


--
-- Name: idx_weather_data_temperature; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_weather_data_temperature ON public.weather_data USING btree (temperature);


--
-- Name: idx_weather_data_time; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_weather_data_time ON public.weather_data USING btree (observation_time DESC);


--
-- Name: idx_weather_forecast_location; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_weather_forecast_location ON public.weather_forecast USING btree (location);


--
-- Name: idx_weather_forecast_time; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_weather_forecast_time ON public.weather_forecast USING btree (forecast_time DESC);


--
-- Name: idx_weather_settings_key; Type: INDEX; Schema: public; Owner: openclaw
--

CREATE INDEX idx_weather_settings_key ON public.weather_settings USING btree (setting_key);


--
-- Name: logs logs_agent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.logs
    ADD CONSTRAINT logs_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES public.agents(agent_id) ON DELETE SET NULL;


--
-- Name: messages messages_agent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES public.agents(agent_id) ON DELETE SET NULL;


--
-- Name: messages messages_conversation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(conversation_id) ON DELETE CASCADE;


--
-- Name: session_state session_state_conversation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.session_state
    ADD CONSTRAINT session_state_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(conversation_id) ON DELETE CASCADE;


--
-- Name: session_state session_state_current_agent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.session_state
    ADD CONSTRAINT session_state_current_agent_id_fkey FOREIGN KEY (current_agent_id) REFERENCES public.agents(agent_id) ON DELETE SET NULL;


--
-- Name: system_metrics system_metrics_agent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.system_metrics
    ADD CONSTRAINT system_metrics_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES public.agents(agent_id) ON DELETE SET NULL;


--
-- Name: tasks tasks_assigned_agent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_assigned_agent_id_fkey FOREIGN KEY (assigned_agent_id) REFERENCES public.agents(agent_id) ON DELETE SET NULL;


--
-- Name: tasks tasks_conversation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: openclaw
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES public.conversations(conversation_id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict w1mE7sGcCiPxngAcYKnw0iTZf0pIkM8h9dLOiZxxaZRFWV7sypdMqwlUI6rTxBf

