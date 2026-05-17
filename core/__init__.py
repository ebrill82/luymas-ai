"""
core — Luymas AI Core Modules

All core subsystems for the Luymas AI multi-agent platform.
"""

from core.orchestrator import (
    AgentInfo,
    AgentStatus,
    ApprovalPipeline,
    ApprovalRequest,
    Message,
    MessagePriority,
    Orchestrator,
    ProjectContext,
    Task,
    TaskScheduler,
    Workflow,
    WorkflowEngine,
    WorkflowStage,
    AgentRegistry,
    MessageRouter,
)

from core.messenger import (
    ContactInfo,
    GroupInfo,
    Messenger,
    MessengerCredentials,
    MessengerGateway,
    MessengerMessage,
    MessageFormat,
    MessageFormatter,
    Platform,
    TelegramGateway,
    WhatsAppGateway,
    GroupManager,
    ContactWhitelist,
)

from core.memory import (
    Experience,
    KnowledgeMesh,
    KnowledgeGraph,
    MemoryEntry,
    MemoryStore,
    MemoryType,
    ProjectHistory,
    SearchResult,
    ExperienceStore,
    KnowledgeMeshExporter,
)

from core.pdf_generator import (
    ArchitectureReport,
    DeploymentReport,
    ExecutiveSummary,
    LessonsLearned,
    PDFGenerator,
    ProjectData,
    SecurityReport,
    SourcesReport,
    TestResultsReport,
)

from core.api_injector import (
    APIInjector,
    APIKey,
    HealthStatus,
    InjectionEngine,
    KeyGenerator,
    KeyRegistry,
    HealthCheckClient,
)

from core.auto_updater import (
    AutoUpdater,
    ChangeEntry,
    ChangeLog,
    UpdateApplier,
    UpdateDetector,
    UpdateProposal,
    UpdateStatus,
    UpdateType,
)

from core.github_scout import (
    AnalysisReport,
    GitHubScout,
    LicenseChecker,
    LicenseType,
    ProjectAnalyzer,
    ProjectSearcher,
    SearchResult as GitHubSearchResult,
    SourceEntry,
    SourceDocumenter,
)

from core.self_improver import (
    CodeOptimizer,
    CodeProposal,
    ImprovementCycle,
    ModelUpdate,
    Proposal,
    ProposalGenerator,
    ProposalStatus,
    ProposalType,
    SelfImprover,
    ModelUpdater,
)

from core.experience_learner import (
    ExperienceLearner,
    Lesson,
    Pattern,
    PatternType,
    PreProjectAdvisor,
    ProjectOutcome,
    Recommendation,
    Retrospective,
    RetrospectiveAnalyzer,
    PatternDetector,
    LessonExtractor,
    KnowledgeUpdater,
)

from core.email_factory import (
    AliasKitProvider,
    EmailAccount,
    EmailClient,
    EmailManager,
    EmailMessage,
    EmailProvider,
    EmailProviderBase,
    EmailStatus,
    GmailProvider,
    MailgunProvider,
    ProtonMailProvider,
)

from core.captcha_solver import (
    CaptchaDetector,
    CaptchaInfo,
    CaptchaSolver,
    CaptchaType,
    CloudflareBypasser,
    HelpRequest,
    HumanHelper,
    SolveResult,
    SolveStatus,
    AudioCaptchaSolver,
    ImageCaptchaSolver,
    TextCaptchaSolver,
)

from core.identity_manager import (
    AccountCreator,
    AuditEntry,
    AuditTrail,
    Identity,
    IdentityCreator,
    IdentityManager,
    IdentityRegistry,
    IdentityRevoker,
    IdentityStatus,
    ServiceAccount,
    ServiceType,
)

__all__ = [
    # orchestrator
    "AgentInfo", "AgentStatus", "ApprovalPipeline", "ApprovalRequest",
    "Message", "MessagePriority", "Orchestrator", "ProjectContext",
    "Task", "TaskScheduler", "Workflow", "WorkflowEngine",
    "WorkflowStage", "AgentRegistry", "MessageRouter",
    # messenger
    "ContactInfo", "GroupInfo", "Messenger", "MessengerCredentials",
    "MessengerGateway", "MessengerMessage", "MessageFormat",
    "MessageFormatter", "Platform", "TelegramGateway", "WhatsAppGateway",
    "GroupManager", "ContactWhitelist",
    # memory
    "Experience", "KnowledgeMesh", "KnowledgeGraph", "MemoryEntry",
    "MemoryStore", "MemoryType", "ProjectHistory", "SearchResult",
    "ExperienceStore", "KnowledgeMeshExporter",
    # pdf_generator
    "ArchitectureReport", "DeploymentReport", "ExecutiveSummary",
    "LessonsLearned", "PDFGenerator", "ProjectData", "SecurityReport",
    "SourcesReport", "TestResultsReport",
    # api_injector
    "APIInjector", "APIKey", "HealthStatus", "InjectionEngine",
    "KeyGenerator", "KeyRegistry", "HealthCheckClient",
    # auto_updater
    "AutoUpdater", "ChangeEntry", "ChangeLog", "UpdateApplier",
    "UpdateDetector", "UpdateProposal", "UpdateStatus", "UpdateType",
    # github_scout
    "AnalysisReport", "GitHubScout", "LicenseChecker", "LicenseType",
    "ProjectAnalyzer", "ProjectSearcher", "GitHubSearchResult",
    "SourceEntry", "SourceDocumenter",
    # self_improver
    "CodeOptimizer", "CodeProposal", "ImprovementCycle", "ModelUpdate",
    "Proposal", "ProposalGenerator", "ProposalStatus", "ProposalType",
    "SelfImprover", "ModelUpdater",
    # experience_learner
    "ExperienceLearner", "Lesson", "Pattern", "PatternType",
    "PreProjectAdvisor", "ProjectOutcome", "Recommendation",
    "Retrospective", "RetrospectiveAnalyzer", "PatternDetector",
    "LessonExtractor", "KnowledgeUpdater",
    # email_factory
    "AliasKitProvider", "EmailAccount", "EmailClient", "EmailManager",
    "EmailMessage", "EmailProvider", "EmailProviderBase", "EmailStatus",
    "GmailProvider", "MailgunProvider", "ProtonMailProvider",
    # captcha_solver
    "CaptchaDetector", "CaptchaInfo", "CaptchaSolver", "CaptchaType",
    "CloudflareBypasser", "HelpRequest", "HumanHelper", "SolveResult",
    "SolveStatus", "AudioCaptchaSolver", "ImageCaptchaSolver",
    "TextCaptchaSolver",
    # identity_manager
    "AccountCreator", "AuditEntry", "AuditTrail", "Identity",
    "IdentityCreator", "IdentityManager", "IdentityRegistry",
    "IdentityRevoker", "IdentityStatus", "ServiceAccount", "ServiceType",
]
