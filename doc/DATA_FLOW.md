# 🔍 Chatbot PSB - Data Flow Diagrams

Visual representations of data and control flow throughout the system.

---

## Complete Request-Response Flow Diagram

```mermaid
sequenceDiagram
    participant User as 👤 User<br/>(Telegram)
    participant TBot as 📱 Telegram<br/>Bot API
    participant FastAPI as 🌐 FastAPI<br/>Server
    participant TBH as 📨 Telegram<br/>Bot Handler
    participant Router as 🎯 Response<br/>Router
    participant IC as 🧠 Intent<br/>Classifier
    participant KB as 📚 Knowledge<br/>Base
    participant Groq as 🤖 Groq<br/>LLM API
    participant DB as 💾 Database

    User->>TBot: Send message
    TBot->>FastAPI: POST /webhook
    FastAPI->>TBH: process_update()
    TBH->>Router: process_question()
    
    rect rgb(100, 200, 255)
        Note over IC: GUARD LAYER 1
        Router->>IC: predict(question)
        IC->>IC: TF-IDF vectorize
        IC->>IC: Logistic Regression
        IC-->>Router: IntentPrediction
    end
    
    Router->>KB: Load KB by intent
    KB-->>Router: KB data
    
    rect rgb(255, 200, 100)
        Note over Groq: GUARD LAYER 2
        Router->>Groq: generate_response()
        Groq->>Groq: Build system prompt
        Groq->>Groq: Add guardrails
        Groq->>Groq: Send to LLaMA API
        Groq-->>Router: GroqResponse
    end
    
    Router->>DB: log_user_question()
    DB-->>Router: question_id
    
    Router-->>TBH: ResponseResult
    TBH->>TBot: sendMessage()
    TBot->>User: Display message
    User->>User: Read response
```

---

## Intent Classification Pipeline

```mermaid
flowchart TD
    A["📝 User Question<br/>Input: string"] 
    
    B["🔤 Text Preprocessing<br/>- Lowercase<br/>- Trim / collapse whitespace"]
    
    C["📊 TF-IDF Vectorization<br/>- Convert to numerical features<br/>- Training: max_features=3000, ngram (1,2)"]
    
    D["🧮 Logistic Regression<br/>- Predict class<br/>- Calculate probabilities<br/>- Get confidence score"]
    
    E["🏷️ Decode Labels<br/>- Map numeric labels<br/>to intent names"]
    
    F["✅ Confidence Check<br/>Score ≥ 0.7?"]
    
    G["📌 High Confidence<br/>is_confident=True"]
    
    H["⚠️ Low Confidence<br/>is_confident=False"]
    
    I["🎯 IntentPrediction<br/>- intent: str<br/>- confidence: float<br/>- all_probabilities: dict<br/>- is_confident: bool"]
    
    A --> B --> C --> D --> E --> F
    F -->|Yes| G --> I
    F -->|No| H --> I
    
    style A fill:#e1f5ff
    style I fill:#c8e6c9
    style F fill:#fff9c4
```

---

## Confidence-Based Response Selection Flow

```mermaid
flowchart TD
    A["🎯 Get Intent Prediction<br/>confidence from Guard 1"]
    
    B{"Confidence ≥ 0.7?<br/>HIGH"}
    
    C["✅ Use Full Pipeline<br/>- Load KB<br/>- Call Groq LLM<br/>- Refine response"]
    
    D{"0.5 ≤ Confidence < 0.7?<br/>MEDIUM"}
    
    E["⚠️ Use Cautious Pipeline<br/>- Load KB<br/>- Use KB data only<br/>- Skip Groq if risky"]
    
    F{"Confidence < 0.5?<br/>LOW"}
    
    G["❌ Use Fallback<br/>- Best match with disclaimer<br/>- Offer escalation<br/>- Log for review"]
    
    H["📨 Send Response"]
    
    A --> B
    B -->|Yes| C
    B -->|No| D
    D -->|Yes| E
    D -->|No| F
    F -->|Yes| G
    
    C --> H
    E --> H
    G --> H
    
    style B fill:#fff9c4
    style D fill:#ffe0b2
    style F fill:#ffccbc
```

---

## Error Handling & Fallback Strategy

```mermaid
flowchart TD
    A["🔧 Processing Question"]
    
    B{"Intent Classifier<br/>Success?"}
    
    C["✅ Get Intent"]
    
    D["Load Knowledge<br/>Base File"]
    
    E{"KB File<br/>Exists?"}
    
    F["✅ Load KB Data"]
    
    G{"Groq API<br/>Available?"}
    
    H["✅ Call Groq API<br/>Get refined response"]
    
    I["❌ Groq Failed<br/>Use KB without LLM"]
    
    J["❌ KB Not Found<br/>Use generic message"]
    
    K["❌ Classifier Failed<br/>Use fallback intent"]
    
    L["📨 Send Response<br/>to User"]
    
    M["💾 Log to Database"]
    
    A --> B
    B -->|Yes| C --> D --> E
    B -->|No| K
    
    E -->|Yes| F --> G
    E -->|No| J
    
    G -->|Yes| H --> L
    G -->|No| I --> L
    
    K --> L
    J --> L
    
    L --> M
    
    style H fill:#c8e6c9
    style I fill:#ffe0b2
    style J fill:#ffccbc
    style K fill:#ffccbc
```

---

## Data Flow: From Question to Database

```mermaid
flowchart LR
    subgraph Input
        A["📱 Telegram Message"]
    end
    
    subgraph Processing
        B["Parse Message"]
        C["Extract Text"]
        D["Classify Intent"]
        E["Load KB"]
        F["Generate Response"]
    end
    
    subgraph Storage
        G["Create Question Record"]
        H["Insert to DB"]
        I["Return ID"]
    end
    
    subgraph Output
        J["Send to Telegram"]
    end
    
    A --> B --> C --> D --> E --> F
    F --> G --> H --> I
    F --> J
    
    style Input fill:#e1f5ff
    style Processing fill:#fff9c4
    style Storage fill:#c8e6c9
    style Output fill:#c8e6c9
```

---

## Component Interaction Diagram

```mermaid
graph TB
    subgraph External["🌐 External Systems"]
        Telegram["Telegram Bot API"]
        Groq["Groq LLM API"]
        PG["PostgreSQL DB"]
    end
    
    subgraph Application["🎯 Application Layer"]
        FastAPI["FastAPI Server"]
        TelegramBot["Telegram Bot Handler"]
        ResponseRouter["Response Router<br/>(Orchestrator)"]
    end
    
    subgraph Guards["🛡️ Guard Layers"]
        IC["Intent Classifier<br/>(Guard 1)"]
        GC["Groq Client<br/>(Guard 2)"]
    end
    
    subgraph Data["📦 Data Sources"]
        KB["Knowledge Base<br/>(JSON files)"]
        Models["ML Models<br/>(.pkl files)"]
    end
    
    Telegram -->|Webhook| FastAPI
    FastAPI --> TelegramBot
    TelegramBot --> ResponseRouter
    
    ResponseRouter --> IC
    ResponseRouter --> GC
    ResponseRouter --> KB
    
    IC --> Models
    
    GC --> Groq
    Groq --> GC
    
    ResponseRouter --> PG
    PG --> ResponseRouter
    
    TelegramBot --> Telegram
    
    style Guards fill:#fff9c4
    style External fill:#ffccbc
    style Application fill:#c8e6c9
    style Data fill:#b3e5fc
```

---

## Knowledge Base Loading Process

```mermaid
flowchart TD
    A["🎯 Get Predicted Intent<br/>Example: biaya_pendidikan"]
    
    B["📂 Build File Path<br/>knowledge_base/biaya_pendidikan.json"]
    
    C{"File Exists?"}
    
    D["✅ Read JSON File<br/>Parse structure"]
    
    E["📊 Extract Data<br/>- intent: string<br/>- description: string<br/>- items: array"]
    
    F["❌ Return Empty KB<br/>intent: intent_name<br/>data: empty"]
    
    G["🎯 Knowledge Base Data<br/>Ready for LLM"]
    
    A --> B --> C
    C -->|Yes| D --> E --> G
    C -->|No| F --> G
    
    style D fill:#c8e6c9
    style F fill:#ffccbc
    style G fill:#b3e5fc
```

---

## Request Validation & Sanitization Flow

```mermaid
flowchart TD
    A["📨 Receive Telegram Update<br/>Webhook POST"]
    
    B{"Has Required<br/>Fields?"}
    
    C["✅ Extract message<br/>chat_id, user_id, text"]
    
    D["🔤 Sanitize Input<br/>- Strip whitespace<br/>- Truncate to 1000 chars<br/>- Remove null bytes"]
    
    E["✅ Valid Input"]
    
    F["❌ Invalid Format<br/>Log error<br/>Return 400"]
    
    G["🎯 Process Question"]
    
    A --> B
    B -->|Yes| C --> D --> E --> G
    B -->|No| F
    
    style E fill:#c8e6c9
    style F fill:#ffccbc
```

---

## Database Entity Relationships

```mermaid
erDiagram
    USER_QUESTIONS {
        int id PK
        string user_id FK
        string platform
        string question
        string intent
        float confidence
        string response
        datetime timestamp
        string username
        string feedback
        boolean is_correct
    }
    
    USER_QUESTIONS ||--o{ FEEDBACK: has
    
    FEEDBACK {
        int id PK
        int question_id FK
        string user_feedback
        boolean helpful
        datetime created_at
    }
```

---

## System State & Persistence

```mermaid
flowchart TD
    A["🚀 Application Startup"]
    
    B["⚙️ Initialize Components<br/>- Load models (vectorizer, classifier)<br/>- Connect to Groq API<br/>- Initialize database engine"]
    
    C["📝 Models in Memory<br/>- TF-IDF Vectorizer<br/>- Logistic Regression<br/>- Label Encoder"]
    
    D["💾 Database Connected<br/>Ready for logging"]
    
    E["📱 Telegram Handler<br/>Ready for webhooks"]
    
    F["🎯 Request Processing<br/>Use in-memory models<br/>Log results to DB"]
    
    G["🛑 Graceful Shutdown<br/>- Close DB connections<br/>- Cleanup resources<br/>- Flush logs"]
    
    A --> B
    B --> C
    B --> D
    B --> E
    C & D & E --> F
    F --> G
    
    style C fill:#c8e6c9
    style D fill:#c8e6c9
    style E fill:#c8e6c9
```

---

## Response Quality Assurance Flow

```mermaid
flowchart TD
    A["📝 Initial Response<br/>from Groq LLM"]
    
    B["✅ Validation Check<br/>1. Intent maintained?<br/>2. Follows guardrails?<br/>3. Proper format?"]
    
    C{"All Checks<br/>Pass?"}
    
    D["✅ Return Response<br/>Quality assured"]
    
    E["⚠️ Response Issues<br/>- Intent changed<br/>- Invalid format<br/>- Hallucination detected"]
    
    F["🔧 Fallback to KB<br/>Use knowledge base only<br/>Without LLM refinement"]
    
    G["📨 Send to User"]
    
    A --> B --> C
    C -->|Yes| D --> G
    C -->|No| E --> F --> G
    
    style D fill:#c8e6c9
    style F fill:#ffe0b2
```

---

## Concurrent Request Handling

```mermaid
flowchart TD
    A["📱 Multiple Users<br/>Send Questions"]
    
    B["🔀 FastAPI Event Loop<br/>Handle concurrently"]
    
    C["📨 Request 1"]
    D["📨 Request 2"]
    E["📨 Request 3"]
    
    F["🧠 Shared Intent Classifier<br/>In-memory models"]
    
    G["🤖 Groq API Calls<br/>Sequential with rate limits"]
    
    H["💾 Database Pool<br/>Multiple connections"]
    
    A --> B
    B --> C & D & E
    
    C & D & E --> F
    C & D & E --> G
    C & D & E --> H
    
    F -.->|Singleton| F
    G --> |Rate limited| G
    H -.->|Connection pool| H
    
    style F fill:#c8e6c9
    style G fill:#fff9c4
    style H fill:#b3e5fc
```

---

## Confidence Score Distribution

```mermaid
graph LR
    A["🎯 Predicted Confidence<br/>0.0 - 1.0"] -->|0.0-0.2| B["Very Low<br/>Don't use"]
    A -->|0.2-0.5| C["Low<br/>Demo mode with disclaimer"]
    A -->|0.5-0.7| D["Medium<br/>Use KB cautiously"]
    A -->|0.7-0.9| E["High<br/>Use full pipeline"]
    A -->|0.9-1.0| F["Very High<br/>High confidence response"]
    
    style B fill:#ffccbc
    style C fill:#ffccbc
    style D fill:#ffe0b2
    style E fill:#c8e6c9
    style F fill:#81c784
```

---

## Guardrail Enforcement Points

```mermaid
flowchart TD
    A["📝 User Question Received"]
    
    B["🛡️ GUARD 1: Intent Classifier<br/>- Determines answer space<br/>- Confidence validation<br/>- Prevents random answers"]
    
    C["🛡️ GUARD 2: Knowledge Base<br/>- Only factual data<br/>- No information creation<br/>- Scope limiting"]
    
    D["🛡️ GUARD 3: LLM System Prompt<br/>- Can't change intent<br/>- Must use KB only<br/>- Domain restriction"]
    
    E["🛡️ GUARD 4: Response Validation<br/>- Check intent preserved<br/>- Verify KB adherence<br/>- Format validation"]
    
    F["📨 Safe Response"]
    
    A --> B --> C --> D --> E --> F
    
    style B fill:#fff9c4
    style C fill:#fff9c4
    style D fill:#fff9c4
    style E fill:#fff9c4
    style F fill:#c8e6c9
```

---

## Production Deployment Data Flow

```mermaid
graph LR
    subgraph User["User Devices"]
        T1["Telegram"]
    end
    
    subgraph Railway["Railway.app"]
        direction TB
        WEB["Web Service<br/>FastAPI"]
        DB["PostgreSQL<br/>Database"]
    end
    
    subgraph API["External APIs"]
        TAPI["Telegram API"]
        GROQ["Groq API<br/>LLaMA 3.3"]
    end
    
    T1 <-->|WebSocket| TAPI
    TAPI -->|Webhook| WEB
    WEB -->|Query/Log| DB
    WEB -->|Request| GROQ
    GROQ -->|Response| WEB
    WEB -->|sendMessage| TAPI
    TAPI <-->|Display| T1
    
    style WEB fill:#c8e6c9
    style DB fill:#b3e5fc
    style GROQ fill:#fff9c4
```

---

**These diagrams show how data flows through the system at different levels of abstraction.**

