"""
Seed script to populate TalentIQ with 35+ realistic candidates and 35+ diverse jobs.
Calculates semantic embeddings and pre-calculates candidate-job match analytics.
"""

import sys
from pathlib import Path

# Add backend root to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models.candidate import Candidate
from app.models.candidate_experience import CandidateExperience
from app.models.job import Job
from app.services.embedding_service import generate_embedding
from app.services.profile_text_service import (
    build_candidate_profile,
    build_job_profile,
)
from app.services.matching_service import calculate_and_persist_job_matches


CANDIDATES_SEED = [
    {
        "full_name": "Priya Sharma",
        "email": "priya.sharma@alumni.sydney.edu.au",
        "phone": "+61 412 345 678",
        "skills": ["Python", "PyTorch", "TensorFlow", "NLP", "LLMs", "Transformers", "Scikit-Learn", "FastAPI"],
        "experience_years": 1.5,
        "resume_text": "Master of Computer Science (AI Specialization) graduate from University of Sydney. Hands-on experience fine-tuning HuggingFace Transformer models, deploying FastAPI endpoints for inference, and building RAG pipelines using LangChain and ChromaDB.",
        "experiences": [
            {
                "company": "USYD AI Research Lab",
                "role": "AI Research Assistant",
                "start_date": "2023-03",
                "end_date": "2024-06",
                "is_current": False,
                "description": "Fine-tuned LLaMA-2 and Mistral models on biomedical datasets. Built high-throughput FastAPI inference microservices with Docker containerization.",
            },
            {
                "company": "TechInnovate Sydney",
                "role": "Machine Learning Intern",
                "start_date": "2024-07",
                "end_date": None,
                "is_current": True,
                "description": "Developed predictive classification pipelines using PyTorch and Scikit-Learn. Automated feature extraction workflows with Pandas and NumPy.",
            }
        ]
    },
    {
        "full_name": "Liam Chen",
        "email": "liam.chen.dev@outlook.com",
        "phone": "+61 423 456 789",
        "skills": ["React", "TypeScript", "Node.js", "Next.js", "TailwindCSS", "PostgreSQL", "Docker", "REST APIs"],
        "experience_years": 3.0,
        "resume_text": "Fullstack Software Engineer with 3 years of production experience building high-performance web applications with React, TypeScript, Next.js, and Node.js. Skilled in PostgreSQL schema design, Redis caching, and Dockerized deployments.",
        "experiences": [
            {
                "company": "Apex Digital Labs",
                "role": "Fullstack Software Engineer",
                "start_date": "2022-01",
                "end_date": "2024-02",
                "is_current": False,
                "description": "Engineered responsive web applications in React 18, TypeScript, and TailwindCSS. Built Node.js microservices with PostgreSQL and Redis caching.",
            },
            {
                "company": "Canva Partner Studio",
                "role": "Frontend Engineer",
                "start_date": "2024-03",
                "end_date": None,
                "is_current": True,
                "description": "Optimized Core Web Vitals and component architecture for real-time collaborative canvas tools using TypeScript and WebSockets.",
            }
        ]
    },
    {
        "full_name": "Sophia Rodriguez",
        "email": "sophia.rodriguez@dataengine.io",
        "phone": "+61 434 567 890",
        "skills": ["Python", "Apache Spark", "SQL", "Airflow", "Snowflake", "AWS", "dbt", "Docker", "Kafka"],
        "experience_years": 4.0,
        "resume_text": "Senior Data Engineer specializing in distributed data processing, automated ETL/ELT pipelines, and modern data stack (Snowflake, dbt, Apache Airflow, Spark). Proven track record managing multi-terabyte data warehouses on AWS.",
        "experiences": [
            {
                "company": "DataStream Analytics",
                "role": "Data Engineer",
                "start_date": "2021-02",
                "end_date": "2023-08",
                "is_current": False,
                "description": "Architected petabyte-scale data pipelines using PySpark on AWS EMR and orchestrated nightly DAGs with Apache Airflow.",
            },
            {
                "company": "Fintech Solutions Sydney",
                "role": "Senior Data Platform Engineer",
                "start_date": "2023-09",
                "end_date": None,
                "is_current": True,
                "description": "Implemented modern data warehouse on Snowflake with dbt data modeling and Kafka streaming ingestion.",
            }
        ]
    },
    {
        "full_name": "Ethan Patel",
        "email": "ethan.patel.cv@gmail.com",
        "phone": "+61 445 678 901",
        "skills": ["Python", "OpenCV", "PyTorch", "CUDA", "YOLO", "C++", "TensorFlow", "Computer Vision", "Docker"],
        "experience_years": 2.5,
        "resume_text": "Computer Vision Engineer with deep expertise in real-time object detection, segmentation, and edge AI deployment. Experienced with PyTorch, YOLOv8, OpenCV, TensorRT, and CUDA acceleration on NVIDIA Jetson devices.",
        "experiences": [
            {
                "company": "VisionTech Australia",
                "role": "Computer Vision Specialist",
                "start_date": "2022-06",
                "end_date": "2024-04",
                "is_current": False,
                "description": "Trained and optimized custom YOLO models achieving 94% mAP for industrial defect detection. Deployed on Jetson Orin with TensorRT.",
            },
            {
                "company": "Autonomous Systems Hub",
                "role": "Perception Engineer",
                "start_date": "2024-05",
                "end_date": None,
                "is_current": True,
                "description": "Developed LiDAR and camera fusion algorithms in C++ and Python for indoor drone navigation.",
            }
        ]
    },
    {
        "full_name": "Emma Watson",
        "email": "emma.watson.cloud@devops.net",
        "phone": "+61 456 789 012",
        "skills": ["Kubernetes", "Docker", "Terraform", "AWS", "CI/CD", "Prometheus", "Grafana", "Go", "Python", "Linux"],
        "experience_years": 5.0,
        "resume_text": "DevOps & Cloud Platform Engineer with 5 years experience designing resilient Kubernetes clusters on AWS (EKS), automated Infrastructure as Code using Terraform, and building zero-downtime GitHub Actions CI/CD pipelines.",
        "experiences": [
            {
                "company": "CloudScale Australia",
                "role": "DevOps Engineer",
                "start_date": "2020-01",
                "end_date": "2022-12",
                "is_current": False,
                "description": "Managed multi-region AWS infrastructure with Terraform, reducing cloud costs by 30% and standardizing Docker containers.",
            },
            {
                "company": "Atlassian Ecosystem Partner",
                "role": "Senior Site Reliability Engineer",
                "start_date": "2023-01",
                "end_date": None,
                "is_current": True,
                "description": "Scaled production EKS Kubernetes clusters serving 10M+ daily requests. Implemented Prometheus, Grafana, and Datadog monitoring.",
            }
        ]
    },
    {
        "full_name": "Lucas Kim",
        "email": "lucas.kim@gopher.dev",
        "phone": "+61 467 890 123",
        "skills": ["Go", "gRPC", "PostgreSQL", "Redis", "Kafka", "Docker", "Kubernetes", "Microservices", "REST APIs"],
        "experience_years": 3.5,
        "resume_text": "Backend Systems Engineer specializing in Go (Golang), high-concurrency microservices, gRPC inter-service communication, and event-driven architecture using Apache Kafka and PostgreSQL.",
        "experiences": [
            {
                "company": "PaymentRail Sydney",
                "role": "Backend Go Developer",
                "start_date": "2021-08",
                "end_date": "2023-11",
                "is_current": False,
                "description": "Engineered core transaction ledger processing 5,000 TPS in Go with sub-20ms latency and strict ACID compliance.",
            },
            {
                "company": "HyperScale Services",
                "role": "Senior Systems Engineer",
                "start_date": "2023-12",
                "end_date": None,
                "is_current": True,
                "description": "Built event-driven microservices with Kafka, gRPC, and Redis cluster caching, running on Kubernetes.",
            }
        ]
    },
    {
        "full_name": "Olivia Zhang",
        "email": "olivia.zhang.ai@research.edu.au",
        "phone": "+61 478 901 234",
        "skills": ["Python", "LangChain", "LlamaIndex", "OpenAI", "HuggingFace", "FastAPI", "VectorDB", "PyTorch", "Docker"],
        "experience_years": 2.0,
        "resume_text": "AI Engineer and USYD Graduate focused on Generative AI, Retrieval-Augmented Generation (RAG), vector databases (Pinecone, ChromaDB, Qdrant), and agentic workflows using LangGraph and LangChain.",
        "experiences": [
            {
                "company": "Sydney AI Foundry",
                "role": "Generative AI Engineer",
                "start_date": "2023-01",
                "end_date": "2024-05",
                "is_current": False,
                "description": "Built enterprise document search RAG systems with hybrid lexical-vector retrieval and reranking models.",
            },
            {
                "company": "Cognitive Agents Lab",
                "role": "LLM Solutions Architect",
                "start_date": "2024-06",
                "end_date": None,
                "is_current": True,
                "description": "Developed autonomous multi-agent systems using LangGraph, OpenAI function calling, and structured output parsing.",
            }
        ]
    },
    {
        "full_name": "Noah Walker",
        "email": "noah.walker@designcode.com",
        "phone": "+61 489 012 345",
        "skills": ["React", "Vue.js", "TypeScript", "TailwindCSS", "Figma", "GraphQL", "Jest", "HTML5", "CSS3"],
        "experience_years": 3.0,
        "resume_text": "Frontend Software Engineer with a strong design sensibility. Expert in React 18, Vue 3, TypeScript, TailwindCSS, component libraries, design systems, and Web Content Accessibility Guidelines (WCAG 2.1 AA).",
        "experiences": [
            {
                "company": "PixelCraft Agency",
                "role": "Frontend Developer",
                "start_date": "2022-02",
                "end_date": "2023-10",
                "is_current": False,
                "description": "Developed responsive, accessible UI components in React and TypeScript for Fortune 500 client portals.",
            },
            {
                "company": "SaaS Launchpad",
                "role": "Senior UI Engineer",
                "start_date": "2023-11",
                "end_date": None,
                "is_current": True,
                "description": "Created comprehensive Figma-to-code design system and Storybook component catalog adopted by 4 product teams.",
            }
        ]
    },
    {
        "full_name": "Isabella Rossi",
        "email": "isabella.rossi@secops.io",
        "phone": "+61 490 123 456",
        "skills": ["Python", "Bash", "SIEM", "Wireshark", "Penetration Testing", "Linux", "Cryptography", "AWS", "Docker"],
        "experience_years": 2.5,
        "resume_text": "Cybersecurity Analyst and Ethical Hacker skilled in vulnerability assessments, penetration testing, threat hunting, SIEM log analysis (Splunk, Elastic SIEM), and automated security scripting in Python and Bash.",
        "experiences": [
            {
                "company": "CyberShield Australia",
                "role": "Security Operations Analyst",
                "start_date": "2022-09",
                "end_date": "2024-03",
                "is_current": False,
                "description": "Monitored 24/7 SOC alerts, analyzed network packet captures with Wireshark, and mitigated DDOS attacks.",
            },
            {
                "company": "RedTeam Defense Labs",
                "role": "Penetration Tester",
                "start_date": "2024-04",
                "end_date": None,
                "is_current": True,
                "description": "Conducted web application vulnerability testing (OWASP Top 10) and network penetration tests for financial clients.",
            }
        ]
    },
    {
        "full_name": "James Murphy",
        "email": "james.murphy@quantcapital.com.au",
        "phone": "+61 401 234 567",
        "skills": ["C++", "Python", "Multithreading", "Linux", "Low-Latency Systems", "Algorithms", "SQL", "Git"],
        "experience_years": 4.0,
        "resume_text": "Quantitative Software Developer with 4 years building ultra-low-latency market connectivity gateways, high-throughput order execution systems, and statistical arbitrage backtesting engines in C++20 and Python.",
        "experiences": [
            {
                "company": "Sydney Trading Tech",
                "role": "C++ Software Engineer",
                "start_date": "2021-01",
                "end_date": "2023-05",
                "is_current": False,
                "description": "Optimized lock-free ring buffers and SIMD vectorization in C++17, reducing execution latency from 8μs to 1.8μs.",
            },
            {
                "company": "Pacific Alpha Quantitative",
                "role": "Quant Developer",
                "start_date": "2023-06",
                "end_date": None,
                "is_current": True,
                "description": "Maintained direct market access (DMA) exchange order feeds for ASX and SGX trading venues.",
            }
        ]
    },
    {
        "full_name": "Maya Lin",
        "email": "maya.lin.mlops@aiplatform.org",
        "phone": "+61 412 987 654",
        "skills": ["MLflow", "Kubeflow", "Docker", "Kubernetes", "Python", "AWS", "FastAPI", "CI/CD", "PyTorch"],
        "experience_years": 3.0,
        "resume_text": "MLOps Engineer bridging data science and production operations. Experienced in automated model retraining pipelines, MLflow experiment tracking, Kubeflow orchestration, model registry management, and GPU cluster provisioning.",
        "experiences": [
            {
                "company": "DataVanguard",
                "role": "ML Engineer",
                "start_date": "2022-03",
                "end_date": "2023-12",
                "is_current": False,
                "description": "Deployed real-time recommendation models using FastAPI and TorchServe on Kubernetes.",
            },
            {
                "company": "ScaleAI APAC",
                "role": "MLOps Platform Specialist",
                "start_date": "2024-01",
                "end_date": None,
                "is_current": True,
                "description": "Built end-to-end CI/CD pipelines for automated model evaluation, drift detection, and shadow deployment.",
            }
        ]
    },
    {
        "full_name": "Marcus Aurelius Brown",
        "email": "marcus.brown@mobiledesign.io",
        "phone": "+61 423 876 543",
        "skills": ["Flutter", "Dart", "Swift", "Kotlin", "React Native", "Firebase", "REST APIs", "GraphQL", "Git"],
        "experience_years": 3.5,
        "resume_text": "Mobile App Developer with multi-platform mastery in Flutter/Dart, React Native, Swift (iOS), and Kotlin (Android). Published 6+ consumer applications to the App Store and Google Play with over 500k total downloads.",
        "experiences": [
            {
                "company": "AppCraft Sydney",
                "role": "Mobile Developer",
                "start_date": "2021-06",
                "end_date": "2023-07",
                "is_current": False,
                "description": "Built full-featured cross-platform applications using Flutter with offline SQLite synchronization and push notifications.",
            },
            {
                "company": "Fintech Mobile Lab",
                "role": "Lead Mobile Engineer",
                "start_date": "2023-08",
                "end_date": None,
                "is_current": True,
                "description": "Architected banking mobile app in Flutter and Swift with biometric authentication and end-to-end encryption.",
            }
        ]
    },
    {
        "full_name": "Chloe Dupont",
        "email": "chloe.dupont@dataanalytics.com.au",
        "phone": "+61 434 765 432",
        "skills": ["Python", "Pandas", "NumPy", "Tableau", "SQL", "PowerBI", "Scikit-Learn", "Data Visualization"],
        "experience_years": 1.0,
        "resume_text": "Data Analyst and USYD Commerce & Data Science graduate. Skilled in SQL data querying, Python (Pandas/NumPy) statistical modeling, Tableau interactive executive dashboards, and customer segmentation.",
        "experiences": [
            {
                "company": "Sydney Retail Group",
                "role": "Junior Data Analyst",
                "start_date": "2023-11",
                "end_date": None,
                "is_current": True,
                "description": "Developed automated Tableau dashboards tracking marketing campaign ROI and customer retention metrics.",
            }
        ]
    },
    {
        "full_name": "Benjamin Lee",
        "email": "benjamin.lee@distributedsystems.com",
        "phone": "+61 445 654 321",
        "skills": ["Java", "Spring Boot", "Kafka", "Kubernetes", "PostgreSQL", "AWS", "Microservices", "Docker"],
        "experience_years": 7.0,
        "resume_text": "Staff Software Engineer with 7 years of enterprise Java, Spring Boot, and Kafka distributed systems experience. Led high-throughput payment architectures handling millions of daily financial transactions.",
        "experiences": [
            {
                "company": "Enterprise Tech Corp",
                "role": "Senior Backend Engineer",
                "start_date": "2018-02",
                "end_date": "2021-08",
                "is_current": False,
                "description": "Migrated legacy monolithic Java systems to Spring Boot microservices with Kafka message brokers.",
            },
            {
                "company": "Global Payments Australia",
                "role": "Principal Systems Architect",
                "start_date": "2021-09",
                "end_date": None,
                "is_current": True,
                "description": "Led backend architecture for multi-region financial platform with 99.999% SLA and ISO 27001 compliance.",
            }
        ]
    },
    {
        "full_name": "Zara Al-Mansoor",
        "email": "zara.almansoor@roboticslab.org",
        "phone": "+61 456 543 210",
        "skills": ["ROS2", "C++", "Python", "Linux", "Computer Vision", "OpenCV", "SLAM", "Docker"],
        "experience_years": 2.0,
        "resume_text": "Robotics & Autonomous Systems Software Engineer. Experienced in ROS2 (Robot Operating System), LiDAR-based Simultaneous Localization and Mapping (SLAM), C++ real-time path planning, and embedded Linux.",
        "experiences": [
            {
                "company": "USYD Mechatronics & Robotics",
                "role": "Robotics Research Engineer",
                "start_date": "2023-01",
                "end_date": None,
                "is_current": True,
                "description": "Implemented Nav2 autonomous navigation stacks in ROS2 for autonomous warehouse mobile robots.",
            }
        ]
    },
    {
        "full_name": "Daniel Tanaka",
        "email": "daniel.tanaka.genai@deepnet.ai",
        "phone": "+61 467 432 109",
        "skills": ["Python", "PyTorch", "Diffusion Models", "Transformers", "CUDA", "FastAPI", "Docker", "HuggingFace"],
        "experience_years": 3.0,
        "resume_text": "Deep Learning Research Engineer specializing in Generative AI, Latent Diffusion Models (Stable Diffusion, FLUX), transformer architectures, and CUDA GPU optimization.",
        "experiences": [
            {
                "company": "Neural Media AI",
                "role": "Deep Learning Engineer",
                "start_date": "2022-04",
                "end_date": "2024-01",
                "is_current": False,
                "description": "Customized and fine-tuned text-to-image diffusion pipelines with ControlNet conditioning for graphic design workflows.",
            },
            {
                "company": "GenVision Labs",
                "role": "Senior AI Researcher",
                "start_date": "2024-02",
                "end_date": None,
                "is_current": True,
                "description": "Optimized diffusion model inference latencies using TensorRT and vLLM on multi-GPU nodes.",
            }
        ]
    },
    {
        "full_name": "Hannah Schmidt",
        "email": "hannah.schmidt@qadev.de",
        "phone": "+61 478 321 098",
        "skills": ["Python", "Selenium", "Playwright", "Cypress", "CI/CD", "PyTest", "Docker", "Postman"],
        "experience_years": 2.5,
        "resume_text": "Software Development Engineer in Test (SDET) and QA Automation Specialist. Expert in writing robust end-to-end test suites using Playwright, Cypress, and Python PyTest integrated into CI/CD pipelines.",
        "experiences": [
            {
                "company": "QualityFirst Australia",
                "role": "QA Automation Engineer",
                "start_date": "2022-10",
                "end_date": None,
                "is_current": True,
                "description": "Built automated regression testing framework in Playwright and TypeScript covering 95% of core critical checkout paths.",
            }
        ]
    },
    {
        "full_name": "Aarav Gupta",
        "email": "aarav.gupta.research@sydney.edu.au",
        "phone": "+61 489 210 987",
        "skills": ["Python", "PyTorch", "Reinforcement Learning", "Algorithms", "Linear Algebra", "LaTeX", "Docker"],
        "experience_years": 1.0,
        "resume_text": "PhD Student at University of Sydney investigating deep reinforcement learning and model-based policy optimization. Strong mathematical foundations in probability, stochastic processes, and gradient descent algorithms.",
        "experiences": [
            {
                "company": "USYD Machine Learning Lab",
                "role": "Doctoral Researcher",
                "start_date": "2023-08",
                "end_date": None,
                "is_current": True,
                "description": "Authored papers on sample-efficient reinforcement learning algorithms in PyTorch.",
            }
        ]
    },
    {
        "full_name": "Elena Rostova",
        "email": "elena.rostova@dbmasters.net",
        "phone": "+61 490 109 876",
        "skills": ["PostgreSQL", "MySQL", "Redis", "SQL Tuning", "Database Migration", "Linux", "Bash", "Docker"],
        "experience_years": 6.0,
        "resume_text": "Senior Database Administrator & PostgreSQL Specialist. Expert in query performance tuning, index optimization (B-tree, GIN, GiST), high-availability replication, and disaster recovery.",
        "experiences": [
            {
                "company": "Database Scaling Australia",
                "role": "Senior DBA",
                "start_date": "2019-03",
                "end_date": None,
                "is_current": True,
                "description": "Managed 50TB+ PostgreSQL production clusters with Patroni HA, pgBouncer pooling, and automated failover.",
            }
        ]
    },
    {
        "full_name": "Jack Thompson",
        "email": "jack.thompson@web3solidity.io",
        "phone": "+61 401 098 765",
        "skills": ["Solidity", "Ethereum", "Web3.js", "Rust", "Smart Contracts", "Hardhat", "Go", "Git"],
        "experience_years": 3.0,
        "resume_text": "Blockchain & Smart Contract Developer with deep expertise in EVM, Solidity security patterns, DeFi protocols, ERC standards, and Rust smart contract development for Solana.",
        "experiences": [
            {
                "company": "DeFi Protocol Hub",
                "role": "Smart Contract Engineer",
                "start_date": "2022-01",
                "end_date": None,
                "is_current": True,
                "description": "Audited and deployed audited Solidity smart contracts managing over $20M in Total Value Locked (TVL).",
            }
        ]
    },
    {
        "full_name": "Ananya Iyer",
        "email": "ananya.iyer@conversationalai.com",
        "phone": "+61 412 087 654",
        "skills": ["Python", "FastAPI", "NLP", "Prompt Engineering", "LangChain", "OpenAI", "Docker", "REST APIs"],
        "experience_years": 2.0,
        "resume_text": "Conversational AI Engineer specializing in enterprise virtual assistants, dialogue state tracking, prompt engineering, and LLM-powered agent workflows.",
        "experiences": [
            {
                "company": "BotCraft Solutions",
                "role": "Conversational AI Developer",
                "start_date": "2023-02",
                "end_date": None,
                "is_current": True,
                "description": "Built omni-channel customer support AI agents resolving 65% of inbound tier-1 support queries automatically.",
            }
        ]
    },
    {
        "full_name": "Samuel O'Connor",
        "email": "samuel.oconnor@fullstackts.dev",
        "phone": "+61 423 076 543",
        "skills": ["TypeScript", "React", "Node.js", "GraphQL", "PostgreSQL", "Docker", "Next.js", "TailwindCSS"],
        "experience_years": 4.0,
        "resume_text": "Senior Fullstack TypeScript Engineer passionate about modern developer experience, type safety from database to UI, GraphQL APIs, and clean React architecture.",
        "experiences": [
            {
                "company": "SaaS Platform APAC",
                "role": "Senior Fullstack Engineer",
                "start_date": "2021-04",
                "end_date": None,
                "is_current": True,
                "description": "Spearheaded fullstack TypeScript migration using Apollo GraphQL, Prisma ORM, and Next.js App Router.",
            }
        ]
    },
    {
        "full_name": "Grace Kim",
        "email": "grace.kim@productanalytics.com",
        "phone": "+61 434 065 432",
        "skills": ["Python", "SQL", "Pandas", "Scikit-Learn", "A/B Testing", "Tableau", "Statistical Modeling"],
        "experience_years": 3.0,
        "resume_text": "Product Data Scientist with 3 years driving product growth, designing rigorous randomized A/B experimentation frameworks, and customer lifetime value modeling.",
        "experiences": [
            {
                "company": "E-Commerce Growth Lab",
                "role": "Data Scientist",
                "start_date": "2022-03",
                "end_date": None,
                "is_current": True,
                "description": "Designed multi-variant A/B experiments that unlocked a 14% increase in user onboarding conversion rate.",
            }
        ]
    },
    {
        "full_name": "Mateo Fernandez",
        "email": "mateo.fernandez@infrastructure.net",
        "phone": "+61 445 054 321",
        "skills": ["Terraform", "AWS", "Kubernetes", "Linux", "Grafana", "Python", "Docker", "Ansible", "CI/CD"],
        "experience_years": 4.5,
        "resume_text": "Infrastructure & Cloud Architect with extensive experience automating multi-account AWS landing zones, Kubernetes clusters, and monitoring stacks with Prometheus and Grafana.",
        "experiences": [
            {
                "company": "CloudTech Systems",
                "role": "Lead Infrastructure Engineer",
                "start_date": "2020-10",
                "end_date": None,
                "is_current": True,
                "description": "Automated AWS multi-account governance and Terraform module libraries across 40+ engineering teams.",
            }
        ]
    },
    {
        "full_name": "Emily Nguyen",
        "email": "emily.nguyen@computationalbio.org",
        "phone": "+61 456 043 210",
        "skills": ["Python", "R", "Machine Learning", "Scikit-Learn", "SQL", "Docker", "Pandas", "Statistical Modeling"],
        "experience_years": 2.0,
        "resume_text": "Computational Biologist & Data Scientist applying statistical modeling and machine learning algorithms to high-throughput genomic data and biological discovery.",
        "experiences": [
            {
                "company": "Genomics Research Institute",
                "role": "Bioinformatics Scientist",
                "start_date": "2023-01",
                "end_date": None,
                "is_current": True,
                "description": "Developed predictive ML models for gene expression classification using Python and Scikit-Learn.",
            }
        ]
    },
    {
        "full_name": "Joshua David",
        "email": "joshua.david@cloudsecurity.io",
        "phone": "+61 467 032 109",
        "skills": ["AWS", "Terraform", "Python", "Kubernetes", "Linux", "Docker", "CI/CD", "Cybersecurity"],
        "experience_years": 3.5,
        "resume_text": "Cloud Security Engineer focused on DevSecOps, automated compliance scanning (Trivy, SonarQube), AWS IAM least-privilege policy generation, and Kubernetes pod security standards.",
        "experiences": [
            {
                "company": "SecureCloud Systems",
                "role": "Cloud Security Specialist",
                "start_date": "2021-11",
                "end_date": None,
                "is_current": True,
                "description": "Integrated security scanning into CI/CD pipelines, catching over 200 high-severity CVEs before production deploy.",
            }
        ]
    },
    {
        "full_name": "Zoe Taylor",
        "email": "zoe.taylor@reactnative.dev",
        "phone": "+61 478 021 098",
        "skills": ["React", "TypeScript", "Redux", "Jest", "TailwindCSS", "REST APIs", "Git", "HTML5"],
        "experience_years": 2.5,
        "resume_text": "Mobile Frontend Developer specialized in React Native and TypeScript. Passionate about silky-smooth 60fps animations, intuitive UI transitions, and modular Redux state management.",
        "experiences": [
            {
                "company": "AppVentures Sydney",
                "role": "React Native Developer",
                "start_date": "2022-08",
                "end_date": None,
                "is_current": True,
                "description": "Delivered flagship iOS and Android mobile app with 4.8-star App Store rating and 100k active monthly users.",
            }
        ]
    },
    {
        "full_name": "Kavita Reddy",
        "email": "kavita.reddy@bigdata.net",
        "phone": "+61 489 010 987",
        "skills": ["Apache Spark", "Kafka", "Python", "SQL", "AWS", "Snowflake", "Docker", "Java"],
        "experience_years": 5.5,
        "resume_text": "Principal Big Data Architect with 5+ years designing real-time streaming architectures using Apache Spark Streaming, Kafka event backbones, and Snowflake analytical layers.",
        "experiences": [
            {
                "company": "BigData Dynamics",
                "role": "Lead Big Data Engineer",
                "start_date": "2019-06",
                "end_date": None,
                "is_current": True,
                "description": "Designed real-time clickstream processing engine handling 50k events/sec on AWS with Spark and Kafka.",
            }
        ]
    },
    {
        "full_name": "Leo Martinez",
        "email": "leo.martinez@searchrec.io",
        "phone": "+61 490 009 876",
        "skills": ["Python", "VectorDB", "PyTorch", "FastAPI", "Docker", "Scikit-Learn", "PostgreSQL", "REST APIs"],
        "experience_years": 3.5,
        "resume_text": "Search & Recommendation Systems Engineer. Experienced with dense vector search, semantic embeddings, approximate nearest neighbor (ANN) indexes, and two-tower recommendation architectures.",
        "experiences": [
            {
                "company": "SearchAI Labs",
                "role": "Information Retrieval Engineer",
                "start_date": "2021-07",
                "end_date": None,
                "is_current": True,
                "description": "Replaced traditional keyword search with hybrid dense retrieval, improving user click-through rate by 22%.",
            }
        ]
    },
    {
        "full_name": "Mia Anderson",
        "email": "mia.anderson@accessibilityui.org",
        "phone": "+61 401 998 877",
        "skills": ["React", "TypeScript", "HTML5", "CSS3", "TailwindCSS", "Figma", "Jest", "Git"],
        "experience_years": 3.0,
        "resume_text": "Design Systems & Web Accessibility (a11y) Lead. Expert in WCAG 2.1 AAA compliance, screen reader compatibility, keyboard navigation, and composable UI design tokens.",
        "experiences": [
            {
                "company": "Inclusive Web Australia",
                "role": "UI Accessibility Engineer",
                "start_date": "2022-04",
                "end_date": None,
                "is_current": True,
                "description": "Audited and refactored government agency public portals to attain full WCAG 2.1 AA certification.",
            }
        ]
    },
    {
        "full_name": "Oliver Davies",
        "email": "oliver.davies@fastapibackend.com",
        "phone": "+61 412 887 766",
        "skills": ["Python", "FastAPI", "PostgreSQL", "Redis", "Docker", "SQL", "REST APIs", "Git"],
        "experience_years": 4.0,
        "resume_text": "Senior Python Backend Developer with 4 years building asynchronous REST APIs using FastAPI, SQLAlchemy ORM, Alembic migrations, Redis caching, and Docker microservices.",
        "experiences": [
            {
                "company": "CloudAPI Systems",
                "role": "Senior Backend Developer",
                "start_date": "2021-03",
                "end_date": None,
                "is_current": True,
                "description": "Architected high-throughput async FastAPI microservices handling 20M monthly requests with sub-50ms P99 latency.",
            }
        ]
    },
    {
        "full_name": "Aisha Bello",
        "email": "aisha.bello@aisafety.org",
        "phone": "+61 423 776 655",
        "skills": ["Python", "Prompt Engineering", "LLMs", "NLP", "PyTorch", "Docker", "Transformers"],
        "experience_years": 1.5,
        "resume_text": "AI Safety & Red-Teaming Specialist. Experienced in adversarial prompt testing, LLM jailbreak evaluations, guardrail development (NeMo Guardrails, Llama-Guard), and alignment benchmarking.",
        "experiences": [
            {
                "company": "AI Trust & Safety Institute",
                "role": "AI Red-Teamer",
                "start_date": "2023-05",
                "end_date": None,
                "is_current": True,
                "description": "Developed benchmark suite assessing hallucination rates and prompt injection vulnerabilities in frontier LLMs.",
            }
        ]
    },
    {
        "full_name": "Gabriel Santos",
        "email": "gabriel.santos@embeddediot.io",
        "phone": "+61 434 665 544",
        "skills": ["C++", "C", "Linux", "Python", "Git", "Docker", "Microservices"],
        "experience_years": 3.0,
        "resume_text": "Embedded Software & IoT Firmware Engineer. Skilled in C/C++ programming for ARM Cortex microcontrollers, FreeRTOS, MQTT telemetry protocols, and Linux kernel device drivers.",
        "experiences": [
            {
                "company": "SmartSensors Australia",
                "role": "Firmware Engineer",
                "start_date": "2022-02",
                "end_date": None,
                "is_current": True,
                "description": "Wrote ultra-low power firmware in C for battery-operated environmental sensors with 5-year battery life.",
            }
        ]
    },
    {
        "full_name": "Jessica Wang",
        "email": "jessica.wang@growthdata.com",
        "phone": "+61 445 554 433",
        "skills": ["Python", "SQL", "Machine Learning", "Pandas", "Scikit-Learn", "Tableau", "Statistical Modeling"],
        "experience_years": 2.5,
        "resume_text": "Data Scientist specialized in growth analytics, customer churn prediction, recommendation modeling with Scikit-Learn, and interactive business intelligence dashboards.",
        "experiences": [
            {
                "company": "Fintech Scaleup",
                "role": "Growth Data Scientist",
                "start_date": "2022-09",
                "end_date": None,
                "is_current": True,
                "description": "Built XGBoost churn prediction model that helped customer success team save $1.2M in annual recurring revenue.",
            }
        ]
    },
    {
        "full_name": "Ryan Mitchell",
        "email": "ryan.mitchell@cloudarch.com.au",
        "phone": "+61 456 443 322",
        "skills": ["AWS", "Terraform", "Kubernetes", "Docker", "CI/CD", "Python", "Linux", "Microservices"],
        "experience_years": 6.5,
        "resume_text": "Principal Cloud Solutions Architect with 6.5 years designing resilient, secure multi-cloud architectures across AWS and Azure for high-growth enterprise SaaS companies.",
        "experiences": [
            {
                "company": "Enterprise Cloud Global",
                "role": "Cloud Architect",
                "start_date": "2018-06",
                "end_date": None,
                "is_current": True,
                "description": "Spearheaded zero-trust cloud migration for 5 enterprise clients reducing operational overhead by 40%.",
            }
        ]
    },
    {
        "full_name": "Tara O'Sullivan",
        "email": "tara.osullivan@nlplabs.com",
        "phone": "+61 467 332 211",
        "skills": ["Python", "NLP", "PyTorch", "Transformers", "LLMs", "HuggingFace", "FastAPI", "Docker"],
        "experience_years": 2.0,
        "resume_text": "NLP Research Engineer specializing in Named Entity Recognition (NER), relation extraction, BERT transformers, and multilingual text classification pipelines.",
        "experiences": [
            {
                "company": "Linguistic AI Group",
                "role": "NLP Engineer",
                "start_date": "2023-03",
                "end_date": None,
                "is_current": True,
                "description": "Built custom multilingual NER model in PyTorch processing legal contracts with 93% precision.",
            }
        ]
    }
]


JOBS_SEED = [
    {
        "title": "Generative AI & LLM Engineer",
        "company": "Canva",
        "minimum_experience": 2,
        "required_skills": "Python, PyTorch, LLMs, Transformers, FastAPI, Docker, LangChain",
        "description": "Join Canva's AI innovation squad to build next-generation creative tools. You will fine-tune large language and diffusion models, optimize inference with vLLM, and design low-latency RAG systems for millions of global creators.",
    },
    {
        "title": "Senior Fullstack Engineer (React & TypeScript)",
        "company": "Atlassian",
        "minimum_experience": 3,
        "required_skills": "React, TypeScript, Node.js, Next.js, TailwindCSS, PostgreSQL, Docker",
        "description": "Atlassian is looking for a talented Fullstack Engineer to build scalable collaboration experiences. You will own end-to-end features from beautiful React/TypeScript interfaces to resilient Node.js and PostgreSQL backend microservices.",
    },
    {
        "title": "Cloud DevOps & Platform Engineer",
        "company": "Amazon Web Services (AWS)",
        "minimum_experience": 3,
        "required_skills": "AWS, Kubernetes, Terraform, Docker, CI/CD, Prometheus, Linux, Python",
        "description": "Build and maintain hyperscale cloud platform infrastructure on AWS. You will develop automated Terraform modules, manage EKS Kubernetes clusters, and build self-healing CI/CD pipelines.",
    },
    {
        "title": "Senior Data Engineer (Distributed Pipelines)",
        "company": "Databricks",
        "minimum_experience": 4,
        "required_skills": "Python, Apache Spark, SQL, Airflow, Snowflake, AWS, dbt, Kafka",
        "description": "Design and optimize high-throughput distributed data pipelines. You will leverage Apache Spark, Delta Lake, Snowflake, and dbt to process multi-terabyte analytical workloads with zero downtime.",
    },
    {
        "title": "Computer Vision Research Engineer",
        "company": "CSIRO Data61",
        "minimum_experience": 2,
        "required_skills": "Python, OpenCV, PyTorch, CUDA, YOLO, C++, Computer Vision",
        "description": "Data61 is Australia's leading digital research network. We are seeking a Computer Vision Engineer to research and deploy real-time perception models, 3D point cloud processing, and YOLO object detection models.",
    },
    {
        "title": "High-Frequency Quantitative Developer",
        "company": "Optiver",
        "minimum_experience": 3,
        "required_skills": "C++, Python, Multithreading, Linux, Low-Latency Systems, Algorithms, SQL",
        "description": "Design, build, and optimize ultra-low-latency market connectivity gateways in modern C++20 for global financial exchanges. Requires deep knowledge of CPU cache hierarchies, lock-free data structures, and Linux kernel bypass.",
    },
    {
        "title": "Senior Backend Go Engineer",
        "company": "Stripe",
        "minimum_experience": 3,
        "required_skills": "Go, gRPC, PostgreSQL, Redis, Kafka, Docker, Kubernetes, Microservices",
        "description": "Stripe builds the financial infrastructure of the internet. We are looking for Go engineers to scale our core payment ledger, handle mission-critical idempotent transactions, and build resilient distributed systems.",
    },
    {
        "title": "NLP / Information Extraction Engineer",
        "company": "Google Australia",
        "minimum_experience": 2,
        "required_skills": "Python, NLP, PyTorch, Transformers, LLMs, HuggingFace, FastAPI",
        "description": "Work on Google's search and document understanding pipelines. Develop state-of-the-art NLP models for entity extraction, semantic summarization, and multilingual knowledge graph construction.",
    },
    {
        "title": "Cybersecurity Operations & Threat Hunter",
        "company": "Macquarie Group",
        "minimum_experience": 2,
        "required_skills": "Python, Bash, SIEM, Wireshark, Penetration Testing, Linux, Cryptography",
        "description": "Protect Macquarie's global financial operations. You will analyze complex threat telemetry, investigate suspicious network activity, perform vulnerability penetration tests, and automate incident response scripts.",
    },
    {
        "title": "MLOps Platform Specialist",
        "company": "Snowflake",
        "minimum_experience": 3,
        "required_skills": "MLflow, Kubeflow, Docker, Kubernetes, Python, AWS, FastAPI, CI/CD",
        "description": "Empower data science teams with scalable machine learning platform infrastructure. You will manage Kubeflow pipelines, automate model registry and validation gates, and ensure continuous model delivery.",
    },
    {
        "title": "Senior Mobile Engineer (Flutter & Native)",
        "company": "Uber",
        "minimum_experience": 3,
        "required_skills": "Flutter, Dart, Swift, Kotlin, React Native, Firebase, REST APIs",
        "description": "Develop consumer-facing mobile experiences used by millions daily. Optimize real-time geolocation tracking, payment workflows, and smooth 60fps animations across iOS and Android.",
    },
    {
        "title": "Junior AI Research Associate",
        "company": "USYD AI Research Lab",
        "minimum_experience": 1,
        "required_skills": "Python, PyTorch, Machine Learning, Scikit-Learn, Linear Algebra, Algorithms",
        "description": "The University of Sydney Artificial Intelligence Research Lab invites enthusiastic graduates to join our team exploring foundational deep learning, model interpretability, and transformer architectures.",
    },
    {
        "title": "Distributed Systems Architect",
        "company": "Microsoft",
        "minimum_experience": 5,
        "required_skills": "Java, Spring Boot, Kafka, Kubernetes, PostgreSQL, AWS, Microservices",
        "description": "Lead architectural design for high-scale enterprise cloud services at Microsoft. You will define microservices patterns, event streaming topologies with Kafka, and disaster recovery strategies.",
    },
    {
        "title": "Site Reliability Engineer (SRE)",
        "company": "Canva",
        "minimum_experience": 3,
        "required_skills": "Kubernetes, Docker, Terraform, AWS, Prometheus, Grafana, Linux, Python",
        "description": "Keep Canva's visual design suite blazing fast and 99.99% available. Automate infrastructure with Terraform, build Prometheus observability dashboards, and manage Kubernetes multi-cluster routing.",
    },
    {
        "title": "Autonomous Systems & Robotics Engineer",
        "company": "DroneShield",
        "minimum_experience": 2,
        "required_skills": "ROS2, C++, Python, Linux, Computer Vision, OpenCV, SLAM",
        "description": "Develop cutting-edge autonomous counter-drone detection systems. You will implement real-time sensor fusion, computer vision tracking algorithms, and ROS2 navigation pipelines in C++ and Linux.",
    },
    {
        "title": "Deep Learning Researcher (Multimodal AI)",
        "company": "Anthropic",
        "minimum_experience": 3,
        "required_skills": "Python, PyTorch, Diffusion Models, Transformers, CUDA, HuggingFace",
        "description": "Conduct frontier research on multimodal foundation models, visual reasoning, and generative diffusion architectures. Requires strong mathematical rigor and experience training models on large-scale GPU clusters.",
    },
    {
        "title": "Senior PostgreSQL Database Administrator",
        "company": "Commonwealth Bank",
        "minimum_experience": 5,
        "required_skills": "PostgreSQL, MySQL, Redis, SQL Tuning, Database Migration, Linux, Bash",
        "description": "CBA is seeking an experienced PostgreSQL DBA to optimize mission-critical core banking databases, tune complex SQL queries, and implement zero-downtime replication topologies.",
    },
    {
        "title": "Frontend Design Systems Engineer",
        "company": "Figma",
        "minimum_experience": 3,
        "required_skills": "React, TypeScript, TailwindCSS, Figma, HTML5, CSS3, Jest",
        "description": "Build world-class design systems at Figma. You will author accessible, responsive React components with TypeScript, create robust Storybook documentation, and maintain pixel-perfect UX parity.",
    },
    {
        "title": "Cloud Security Engineer",
        "company": "SafetyCulture",
        "minimum_experience": 3,
        "required_skills": "AWS, Terraform, Python, Kubernetes, Linux, Docker, Cybersecurity",
        "description": "Champion security best practices across cloud infrastructure. You will manage IAM roles, conduct container vulnerability audits, and implement automated policy-as-code guardrails in Terraform.",
    },
    {
        "title": "Bioinformatics Machine Learning Scientist",
        "company": "Garvan Institute",
        "minimum_experience": 2,
        "required_skills": "Python, R, Machine Learning, Scikit-Learn, SQL, Pandas, Statistical Modeling",
        "description": "Apply machine learning and genomic analysis to advance personalized cancer medicine. Work with multidisciplinary teams of bioinformaticians, geneticists, and software engineers.",
    },
    {
        "title": "Web3 & Smart Contract Developer",
        "company": "Immutable",
        "minimum_experience": 2,
        "required_skills": "Solidity, Ethereum, Web3.js, Rust, Smart Contracts, Hardhat, Go",
        "description": "Build scalable layer-2 Web3 gaming infrastructure on Ethereum. You will design, test, and deploy secure Solidity smart contracts and high-throughput zero-knowledge rollup APIs.",
    },
    {
        "title": "Conversational AI Engineer",
        "company": "SoundHound",
        "minimum_experience": 2,
        "required_skills": "Python, FastAPI, NLP, Prompt Engineering, LangChain, OpenAI, Docker",
        "description": "Design conversational voice and text AI agents with real-time intent recognition, context-aware dialogue management, and LLM-powered dynamic responses.",
    },
    {
        "title": "Search & Vector Retrieval Engineer",
        "company": "Pinecone",
        "minimum_experience": 3,
        "required_skills": "Python, VectorDB, PyTorch, FastAPI, Docker, Scikit-Learn, PostgreSQL",
        "description": "Build modern semantic search engines powered by vector databases and dense embedding models. Optimize hybrid lexical-vector retrieval and high-throughput vector index querying.",
    },
    {
        "title": "Senior Python Backend Engineer",
        "company": "Employment Hero",
        "minimum_experience": 3,
        "required_skills": "Python, FastAPI, PostgreSQL, Redis, Docker, SQL, REST APIs",
        "description": "Scale Australia's leading HR and payroll platform. You will build asynchronous REST services with FastAPI, optimize database queries in PostgreSQL, and maintain reliable Redis caching.",
    },
    {
        "title": "Product Data Scientist (Experimentation & Growth)",
        "company": "Linktree",
        "minimum_experience": 2,
        "required_skills": "Python, SQL, Pandas, Scikit-Learn, A/B Testing, Tableau, Statistical Modeling",
        "description": "Drive product strategy through empirical data science. You will design randomized A/B experimentation frameworks, build user segmentation models, and identify high-impact growth opportunities.",
    },
    {
        "title": "Embedded IoT & Firmware Engineer",
        "company": "Cochlear",
        "minimum_experience": 3,
        "required_skills": "C++, C, Linux, Python, Docker, Microservices",
        "description": "Help people hear by developing ultra-reliable embedded firmware for next-generation hearing implants. Requires rigorous C/C++ development, RTOS scheduling, and medical device compliance.",
    },
    {
        "title": "QA Automation Lead (SDET)",
        "company": "WiseTech Global",
        "minimum_experience": 3,
        "required_skills": "Python, Playwright, Cypress, Selenium, CI/CD, PyTest, Docker",
        "description": "Establish automated quality assurance frameworks across WiseTech's global logistics platform. You will build Playwright end-to-end test suites and automate continuous test runs in CI/CD.",
    },
    {
        "title": "AI Safety & Alignment Specialist",
        "company": "Sydney AI Centre",
        "minimum_experience": 1,
        "required_skills": "Python, Prompt Engineering, LLMs, NLP, PyTorch, Transformers",
        "description": "Investigate LLM safety, jailbreak prevention, and output alignment. You will conduct adversarial testing and create automated evaluation benchmarks for foundation models.",
    },
    {
        "title": "Big Data & Real-Time Analytics Engineer",
        "company": "Woolworths Digital",
        "minimum_experience": 4,
        "required_skills": "Apache Spark, Kafka, Python, SQL, AWS, Snowflake, Docker",
        "description": "Transform retail supply chain logistics with real-time stream processing. You will build Apache Spark and Kafka pipelines to analyze inventory movements across 1,000+ stores nationally.",
    },
    {
        "title": "Fullstack Next.js Developer",
        "company": "Vercel",
        "minimum_experience": 2,
        "required_skills": "React, TypeScript, Next.js, TailwindCSS, Node.js, GraphQL, PostgreSQL",
        "description": "Build high-performance web applications with the latest Next.js features (Server Components, Server Actions). Collaborate with the open-source community and refine developer workflows.",
    },
    {
        "title": "Computer Vision & Driver Monitoring Engineer",
        "company": "Seeing Machines",
        "minimum_experience": 2,
        "required_skills": "Python, OpenCV, PyTorch, CUDA, Computer Vision, C++, YOLO",
        "description": "Develop life-saving driver monitoring technology. Train real-time face tracking, gaze estimation, and fatigue detection models deployed into automotive cockpits worldwide.",
    },
    {
        "title": "Senior Cloud Infrastructure Architect",
        "company": "Telstra",
        "minimum_experience": 5,
        "required_skills": "AWS, Terraform, Kubernetes, Docker, CI/CD, Python, Linux",
        "description": "Design telecom-grade cloud architecture for Australia's largest telecommunications network. Lead cloud transformation, multi-region failover, and automated IaC rollouts.",
    },
    {
        "title": "Reinforcement Learning Research Fellow",
        "company": "Sydney AI Hub",
        "minimum_experience": 1,
        "required_skills": "Python, PyTorch, Reinforcement Learning, Algorithms, Linear Algebra",
        "description": "Conduct cutting-edge research in deep reinforcement learning, policy gradient methods, and multi-agent coordination. Publish findings in premier venues (NeurIPS, ICML, ICLR).",
    },
    {
        "title": "Backend API Engineer (Python & Microservices)",
        "company": "Deputy",
        "minimum_experience": 3,
        "required_skills": "Python, FastAPI, PostgreSQL, Redis, Docker, REST APIs, SQL",
        "description": "Help millions of shift workers manage their rosters. You will build resilient, high-speed Python APIs with FastAPI and PostgreSQL, ensuring high throughput and strict data security.",
    },
    {
        "title": "Recommendation Systems Engineer",
        "company": "Spotify",
        "minimum_experience": 3,
        "required_skills": "Python, VectorDB, PyTorch, Scikit-Learn, FastAPI, PostgreSQL, Docker",
        "description": "Help music lovers discover their next favorite artist. Build personalized recommendation models, two-tower retrieval networks, and real-time vector similarity search endpoints.",
    }
]


def seed_database():
    print("🌱 Initializing TalentIQ database seed...")
    db: Session = SessionLocal()

    try:
        # 1. Seed Candidates
        print(f"\n📋 Seeding Candidates (Target: {len(CANDIDATES_SEED)})...")
        candidates_created = 0
        candidates_existing = 0

        for cand_data in CANDIDATES_SEED:
            email = cand_data["email"]
            existing = db.query(Candidate).filter(Candidate.email == email).first()

            if existing:
                candidates_existing += 1
                continue

            # Create candidate
            candidate = Candidate(
                full_name=cand_data["full_name"],
                email=cand_data["email"],
                phone=cand_data["phone"],
                resume_text=cand_data["resume_text"],
                skills=cand_data["skills"],
                experience_years=cand_data["experience_years"],
            )

            # Add experiences
            for exp_data in cand_data.get("experiences", []):
                experience = CandidateExperience(
                    company=exp_data["company"],
                    role=exp_data["role"],
                    start_date=exp_data.get("start_date"),
                    end_date=exp_data.get("end_date"),
                    is_current=exp_data.get("is_current", False),
                    description=exp_data.get("description"),
                )
                candidate.experiences.append(experience)

            # Generate semantic profile embedding
            profile_text = build_candidate_profile(candidate)
            candidate.embedding = generate_embedding(profile_text)

            db.add(candidate)
            candidates_created += 1

        db.commit()
        print(f"✅ Candidates Seeded: {candidates_created} newly created, {candidates_existing} already present.")

        # 2. Seed Jobs
        print(f"\n💼 Seeding Jobs (Target: {len(JOBS_SEED)})...")
        jobs_created = 0
        jobs_existing = 0

        for job_data in JOBS_SEED:
            title = job_data["title"]
            company = job_data["company"]

            existing = db.query(Job).filter(Job.title == title, Job.company == company).first()

            if existing:
                jobs_existing += 1
                continue

            job = Job(
                title=job_data["title"],
                company=job_data["company"],
                description=job_data["description"],
                required_skills=job_data["required_skills"],
                minimum_experience=job_data["minimum_experience"],
            )

            # Generate semantic profile embedding
            profile_text = build_job_profile(job)
            job.embedding = generate_embedding(profile_text)

            db.add(job)
            jobs_created += 1

        db.commit()
        print(f"✅ Jobs Seeded: {jobs_created} newly created, {jobs_existing} already present.")

        # 3. Calculate and persist matches for all jobs
        all_jobs = db.query(Job).all()
        total_candidates = db.query(Candidate).count()
        print(f"\n🎯 Pre-calculating AI hybrid matches across {len(all_jobs)} jobs and {total_candidates} candidates...")

        for idx, job in enumerate(all_jobs, start=1):
            matches = calculate_and_persist_job_matches(db=db, job=job)
            print(f"  [{idx}/{len(all_jobs)}] Calculated {len(matches)} matches for '{job.title}' at {job.company}")

        print(f"\n✨ Database seed completed successfully! Total Candidates: {total_candidates}, Total Jobs: {len(all_jobs)}.")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {str(e)}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
