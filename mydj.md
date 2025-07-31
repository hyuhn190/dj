我将分析这个项目的系统结构和组件之间的关系，并用mermaid图表展示系统设计。

## 系统概述

这是一个字幕查找和学习系统，主要功能包括：
1. 搜索和浏览电视剧信息（通过TMDB API）
2. 下载字幕文件（通过OpenSubtitles API）
3. 解析字幕文件
4. 提供单词翻译和文本转语音（TTS）功能

## 系统架构图

```mermaid
graph TD
    A[用户浏览器] --> B[Django Web应用]
    B --> C[URL路由]
    C --> D[Views层]
    D --> E[Services层]
    E --> F[Repositories层]
    E --> G[外部API]
    E --> H[解析器]
    F --> I[文件系统]
    G --> J[TMDB API]
    G --> K[OpenSubtitles API]
    G --> L[翻译服务]
    G --> M[TTS引擎]
    
    subgraph "Django应用"
        B
        C
        D
        E
        F
        G
        H
    end
    
    subgraph "外部服务"
        J
        K
        L
        M
    end
    
    subgraph "存储"
        I
    end
```


## 详细组件关系图

```mermaid
graph 	LR
    subgraph "应用层"
        A[urls.py] --> B[views.py]
    end
    
    subgraph "业务逻辑层"
        B --> C[ShowService]
        B --> D[SubtitleService]
        B --> E[TranslateService]
        B --> F[TTSService]
        B --> G[ParseService]
        
        C --> D
        D --> H[SubtitleRepo]
        F --> I[TTSRepo]
        G --> J[subtitle_parser.py]
    end
    
    subgraph "外部接口层"
        D --> K[subtitles.py]
        C --> L[tmdb.py]
        E --> M[googletrans/deep-translator]
        F --> N[WindowsSAPIBackend]
        K --> O[OpenSubtitles API]
        L --> P[TMDB API]
    end
    
    subgraph "数据存储"
        H --> Q[文件系统 - 字幕]
        I --> R[文件系统 - TTS音频]
        J --> Q
    end
    
    subgraph "异步任务"
        S[task.py] --> D
        S --> F
    end
```


## Django应用结构图

```mermaid
graph TD
    subgraph "finder应用"
        A[apps.py] --> B[urls.py]
        C[models.py]
        D[admin.py]
        E[tests.py]
        F[views.py]
        G[settings.py引用]
        
        B --> F
        
        subgraph "业务服务"
            H[services/]
            H1[show_service.py]
            H2[subtitle_service.py]
            H3[translate_service.py]
            H4[tts_service.py]
            H5[parse_service.py]
        end
        
        subgraph "数据访问"
            I[repo/]
            I1[subtitle_repo.py]
            I2[tts_repo.py]
        end
        
        subgraph "外部接口"
            J[tmdb.py]
            K[subtitles.py]
            L[providers/]
            L1[tts/windows_sapi.py]
        end
        
        subgraph "工具"
            M[subtitle_parser.py]
            N[task.py]
        end
        
        F --> H
        H --> I
        H --> J
        H --> K
        H --> M
        I --> Q[文件系统]
        K --> O[外部API]
        J --> O
        H --> L
        H --> N
    end
    
    subgraph "Django核心"
        G
        P[templates/]
        R[media/]
    end
    
    F --> P
    I --> R
```


## 主要数据流图

```mermaid
graph TD
    A[用户访问剧集页面] --> B[episode_detail视图]
    B --> C[SubtitleService.get_episode_viewdata]
    C --> D[检查本地字幕文件]
    D -->|文件不存在| E[下载整季字幕]
    E --> F[OpenSubtitles API]
    D -->|文件存在| G[解析字幕文件]
    F --> G
    G --> H[subtitle_parser.py]
    H --> I[返回解析后的字幕段落]
    I --> J[渲染到subtitle.html模板]
    
    subgraph "字幕获取流程"
        C
        D
        E
        F
        G
        H
        I
    end
```


## 单词查询功能流程图

```mermaid
graph TD
    A[用户点击单词] --> B[触发翻译API]
    B --> C[translate_word视图]
    C --> D[TranslateService.translate]
    D --> E[检查缓存]
    E -->|缓存未命中| F[GoogleTrans翻译]
    F --> G[失败时使用DeepTranslator]
    G --> H[保存到Redis缓存]
    E -->|缓存命中| H
    H --> I[返回翻译结果]
    
    A --> J[触发TTS API]
    J --> K[tts_word视图]
    K --> L[TTSService.ensure_word_wav]
    L --> M[检查音频文件是否存在]
    M -->|不存在| N[Windows SAPI生成音频]
    M -->|存在| O[返回音频URL]
    N --> O
    
    subgraph "翻译流程"
        C
        D
        E
        F
        G
        H
        I
    end
    
    subgraph "TTS流程"
        K
        L
        M
        N
        O
    end
```


## 异步任务处理图

```mermaid
graph TD
    A[用户请求] --> B[视图处理]
    B --> C[检查资源是否可用]
    C -->|需要生成| D[创建Celery任务]
    D --> E[download_subtitles_task]
    D --> F[generate_tts_task]
    E --> G[后台执行字幕下载]
    F --> H[后台执行TTS生成]
    G --> I[存储到文件系统]
    H --> J[存储到文件系统]
    C -->|资源已存在| K[直接返回结果]
    
    subgraph "异步处理"
        D
        E
        F
        G
        H
        I
        J
    end
```


这套系统采用了清晰的分层架构设计，将业务逻辑、数据访问、外部接口和表示层分离，便于维护和扩展。主要特点包括：

1. **服务层隔离**：每个核心功能都有专门的服务类负责
2. **仓储模式**：统一管理文件系统访问
3. **外部接口封装**：将API调用封装在独立模块中
4. **异步处理**：使用Celery处理耗时任务
5. **缓存机制**：使用Redis缓存翻译结果
6. **可扩展设计**：TTS支持多种后端实现





