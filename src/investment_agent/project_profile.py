from __future__ import annotations

from collections import Counter
import re
from urllib.parse import urlparse

from .models import ProjectProfile, SourceDocument


class ProjectProfileBuilder:
    _AGGREGATOR_DOMAINS = {
        "futard.io",
        "www.futard.io",
        "metadao.fi",
        "www.metadao.fi",
    }
    _SOCIAL_DOMAINS = {
        "x.com",
        "www.x.com",
        "twitter.com",
        "www.twitter.com",
        "t.me",
        "telegram.me",
        "discord.gg",
        "discord.com",
        "www.discord.com",
        "github.com",
        "www.github.com",
        "medium.com",
        "www.medium.com",
    }
    _GENERIC_PATH_TOKENS = {
        "launch",
        "projects",
        "project",
        "fundraise",
        "token",
        "app",
        "home",
        "about",
    }
    _GENERIC_NAME_WORDS = {
        "owned",
        "liquidity",
        "token",
        "protocol",
        "project",
        "launch",
        "roadmap",
        "phase",
        "core",
    }
    _NAME_STOPWORDS = {
        "The",
        "And",
        "For",
        "With",
        "This",
        "That",
        "From",
        "Your",
        "Launch",
        "Project",
        "Token",
        "Crypto",
        "Web3",
        "Privacy",
        "Policy",
        "Terms",
    }
    _CHAIN_PATTERNS = {
        r"\bethereum\b|\beth\b": "Ethereum",
        r"\bsolana\b": "Solana",
        r"\bbase\b": "Base",
        r"\barbitrum\b": "Arbitrum",
        r"\boptimism\b": "Optimism",
        r"\bpolygon\b": "Polygon",
        r"\bbnb chain\b|\bbinance smart chain\b|\bbsc\b": "BNB Chain",
        r"\bavalanche\b": "Avalanche",
        r"\bsui\b": "Sui",
        r"\baptos\b": "Aptos",
        r"\bbitcoin\b": "Bitcoin",
    }
    _CATEGORY_KEYWORDS = {
        "payments": ("payment", "payments", "remittance", "checkout", "merchant"),
        "defi": ("defi", "dex", "lending", "staking", "yield", "liquidity"),
        "infrastructure": ("infrastructure", "sdk", "api", "rollup", "layer 2", "oracle"),
        "gaming": ("game", "gaming", "metaverse"),
        "ai": ("ai", "agent", "llm"),
        "social": ("social", "community", "creator"),
        "data": ("analytics", "data", "indexer"),
        "identity": ("identity", "attestation", "kyc"),
    }

    def build(self, documents: list[SourceDocument]) -> ProjectProfile:
        corpus = " ".join(doc.text for doc in documents)
        urls = self._collect_urls(documents, corpus)

        name = self._infer_name(corpus, documents, website=None)
        name_token = self._name_token(name)

        website = self._select_primary_website(documents, urls, name_token)
        social_links = self._extract_social_links(urls, name_token)

        focused_corpus = self._build_entity_corpus(corpus, name, website, social_links)
        description = self._infer_description(focused_corpus, name) or self._infer_description(corpus, name)

        category, sector_tags = self._infer_category(focused_corpus)
        if category is None:
            category, sector_tags = self._infer_category(corpus)

        stage = self._infer_stage(focused_corpus) or self._infer_stage(corpus)
        token_symbol = self._infer_token_symbol(focused_corpus) or self._infer_token_symbol(corpus)

        chain_focus = self._infer_chains(focused_corpus)
        if not chain_focus:
            chain_focus = self._infer_chains(corpus)

        key_claims = self._extract_key_claims(focused_corpus, name)
        if not key_claims:
            key_claims = self._extract_key_claims(corpus, name)

        resolved_name = name or "Unknown Project"
        resolved_description = description or "No explicit project description extracted from provided sources."
        resolved_category = category or "unknown"

        data_quality = self._build_quality(
            name=name,
            description=description,
            website=website,
            category=category,
            stage=stage,
            token_symbol=token_symbol,
            chain_focus=chain_focus,
            social_links=social_links,
            source_count=len(documents),
        )

        return ProjectProfile(
            name=resolved_name,
            description=resolved_description,
            website=website,
            category=resolved_category,
            sector_tags=sector_tags,
            stage=stage,
            token_symbol=token_symbol,
            chain_focus=chain_focus,
            social_links=social_links,
            key_claims=key_claims,
            data_quality=data_quality,
        )

    def _collect_urls(self, documents: list[SourceDocument], corpus: str) -> list[str]:
        pattern = re.compile(r"https?://[^\s\"'<>\)]+", flags=re.IGNORECASE)
        found = pattern.findall(corpus)
        combined = [doc.source for doc in documents if self._is_url(doc.source)] + found

        unique: list[str] = []
        seen: set[str] = set()
        for url in combined:
            cleaned = url.rstrip(".,;)]}")
            if cleaned and cleaned not in seen:
                unique.append(cleaned)
                seen.add(cleaned)
        return unique

    def _select_primary_website(self, documents: list[SourceDocument], urls: list[str], name_token: str | None) -> str | None:
        candidates = [url for url in urls if self._is_primary_website_candidate(url)]
        if name_token and candidates:
            scored = sorted(
                candidates,
                key=lambda url: self._url_name_score(url, name_token),
                reverse=True,
            )
            if self._url_name_score(scored[0], name_token) > 0:
                return scored[0]
            return None

        if candidates:
            return candidates[0]

        for doc in documents:
            if self._is_url(doc.source) and self._is_primary_website_candidate(doc.source):
                return doc.source
        return None

    def _is_primary_website_candidate(self, url: str) -> bool:
        if not self._is_url(url):
            return False
        host = self._host(url)
        if host in self._AGGREGATOR_DOMAINS or host in self._SOCIAL_DOMAINS:
            return False
        if any(host.endswith(f".{domain}") for domain in self._SOCIAL_DOMAINS):
            return False
        return True

    def _extract_social_links(self, urls: list[str], name_token: str | None) -> dict[str, str]:
        output: dict[str, str] = {}
        for url in urls:
            host = self._host(url)
            if name_token and self._url_name_score(url, name_token) <= 0:
                continue
            if host in {"x.com", "www.x.com", "twitter.com", "www.twitter.com"} and "x" not in output:
                output["x"] = url
            elif host in {"t.me", "telegram.me"} and "telegram" not in output:
                output["telegram"] = url
            elif host in {"discord.gg", "discord.com", "www.discord.com"} and "discord" not in output:
                output["discord"] = url
            elif host in {"github.com", "www.github.com"} and "github" not in output:
                output["github"] = url
            elif "docs" in host and "docs" not in output:
                output["docs"] = url
            elif "gitbook" in host and "docs" not in output:
                output["docs"] = url
            elif host in {"medium.com", "www.medium.com"} and "medium" not in output:
                output["medium"] = url
        return output

    def _infer_name(self, corpus: str, documents: list[SourceDocument], website: str | None) -> str | None:
        slug_candidate = self._infer_name_from_source_slug(documents)
        if slug_candidate:
            return slug_candidate

        for pattern in (
            r"(?i)\b(?:project|protocol|platform|app|dapp|company|startup|name)\s*[:\-]\s*([A-Z][A-Za-z0-9\-\s]{2,40})",
            r"\b([A-Z][A-Za-z0-9]{2,30})\s+(?:Protocol|Network|Labs|Finance|Pay|DAO)\b",
        ):
            match = re.search(pattern, corpus)
            if match:
                candidate = self._clean_name(match.group(1))
                if candidate and not self._is_generic_name(candidate):
                    return candidate

        noun_candidate = self._infer_name_from_frequent_proper_nouns(corpus)
        if noun_candidate:
            return noun_candidate

        if website:
            domain_name = self._domain_label(website)
            if domain_name and not self._is_generic_name(domain_name):
                return domain_name

        return None

    def _infer_name_from_source_slug(self, documents: list[SourceDocument]) -> str | None:
        for doc in documents:
            if not self._is_url(doc.source):
                continue
            parsed = urlparse(doc.source)
            parts = [p for p in parsed.path.split("/") if p]
            for part in parts:
                slug = part.strip().lower()
                if slug in self._GENERIC_PATH_TOKENS:
                    continue
                if not re.fullmatch(r"[a-z0-9\-]{3,40}", slug):
                    continue
                if any(ch.isdigit() for ch in slug) and len(slug) > 14:
                    continue
                if len(slug) >= 24:
                    continue
                cleaned = self._clean_name(slug)
                if cleaned and not self._is_generic_name(cleaned):
                    return cleaned
        return None

    def _infer_name_from_frequent_proper_nouns(self, corpus: str) -> str | None:
        tokens = re.findall(r"\b[A-Z][A-Za-z0-9]{2,24}\b", corpus)
        filtered = [token for token in tokens if token not in self._NAME_STOPWORDS]
        if not filtered:
            return None
        counts = Counter(filtered)
        for best, freq in counts.most_common(5):
            cleaned = self._clean_name(best)
            if freq >= 2 and cleaned and not self._is_generic_name(cleaned):
                return cleaned
        return None

    def _build_entity_corpus(
        self,
        corpus: str,
        name: str | None,
        website: str | None,
        social_links: dict[str, str],
    ) -> str:
        sentences = self._split_sentences(corpus)
        if not sentences:
            return corpus

        tokens: list[str] = []
        if name:
            tokens.append(name.lower())
            name_token = self._name_token(name)
            if name_token:
                tokens.append(name_token)
        if website:
            label = self._domain_label(website)
            if label:
                tokens.append(label.lower())
        for link in social_links.values():
            parts = [p.lower() for p in urlparse(link).path.split("/") if p]
            if parts:
                tokens.append(parts[-1])

        tokens = [token for token in tokens if len(token) >= 3]
        if not tokens:
            return corpus

        selected: list[str] = []
        for sentence in sentences:
            lower = sentence.lower()
            if any(token in lower for token in tokens):
                selected.append(sentence)

        if len(selected) < 2:
            return corpus
        return " ".join(selected)

    def _infer_description(self, corpus: str, name: str | None) -> str | None:
        sentences = self._split_sentences(corpus)
        if not sentences:
            return None

        def sentence_score(sentence: str) -> int:
            text = sentence.lower()
            score = 0
            if name and name.lower() in text:
                score += 4
            if any(keyword in text for keyword in (" is ", "build", "provid", "protocol", "platform", "network", "payment")):
                score += 2
            if any(keyword in text for keyword in ("cookie", "privacy", "terms", "copyright")):
                score -= 3
            if "http" in text:
                score -= 2
            return score

        candidates = [s for s in sentences if 50 <= len(s) <= 260]
        if not candidates:
            return None
        ranked = sorted(candidates, key=sentence_score, reverse=True)
        best = ranked[0].strip()
        return best if best else None

    def _infer_category(self, corpus: str) -> tuple[str | None, list[str]]:
        text = corpus.lower()
        scores: dict[str, int] = {}
        tags: list[str] = []

        for category, keywords in self._CATEGORY_KEYWORDS.items():
            hit_count = 0
            for keyword in keywords:
                count = self._keyword_count(text, keyword)
                if count > 0:
                    hit_count += count
                    tags.append(keyword)
            if hit_count > 0:
                scores[category] = hit_count

        if not scores:
            return None, []

        best = max(scores.items(), key=lambda item: item[1])[0]
        dedup_tags = list(dict.fromkeys(tags))[:8]
        return best, dedup_tags

    def _infer_stage(self, corpus: str) -> str | None:
        text = corpus.lower()
        if "mainnet" in text and any(word in text for word in ("live", "launched", "launch")):
            return "mainnet"
        if "testnet" in text:
            return "testnet"
        if any(word in text for word in ("revenue", "active users", "traction", "volume")):
            return "growth"
        if any(word in text for word in ("seed", "pre-seed", "mvp", "pilot")):
            return "early"
        if any(word in text for word in ("coming soon", "building", "in development")):
            return "pre-launch"
        return None

    @staticmethod
    def _infer_token_symbol(corpus: str) -> str | None:
        for pattern in (
            r"\$([A-Z]{2,10})\b",
            r"(?i)\btoken\s*(?:symbol|ticker)?\s*[:\-]\s*([A-Z]{2,10})\b",
        ):
            match = re.search(pattern, corpus)
            if match:
                return match.group(1).upper()
        return None

    def _infer_chains(self, corpus: str) -> list[str]:
        text = corpus.lower()
        chains: list[str] = []
        for pattern, label in self._CHAIN_PATTERNS.items():
            if re.search(pattern, text) and label not in chains:
                chains.append(label)
        return chains

    def _extract_key_claims(self, corpus: str, name: str | None) -> list[str]:
        sentences = self._split_sentences(corpus)
        keywords = (
            "revenue",
            "users",
            "mainnet",
            "audit",
            "partnership",
            "treasury",
            "runway",
            "governance",
            "integration",
        )
        claims: list[str] = []

        for sentence in sentences:
            clean = sentence.strip()
            if len(clean) < 45 or len(clean) > 220:
                continue
            lower = clean.lower()
            if name and name.lower() in lower:
                claims.append(clean)
                continue
            if any(keyword in lower for keyword in keywords):
                claims.append(clean)
            if len(claims) >= 5:
                break

        unique = list(dict.fromkeys(claims))
        return unique[:5]

    def _build_quality(
        self,
        *,
        name: str | None,
        description: str | None,
        website: str | None,
        category: str | None,
        stage: str | None,
        token_symbol: str | None,
        chain_focus: list[str],
        social_links: dict[str, str],
        source_count: int,
    ) -> dict:
        fields = {
            "name": bool(name),
            "description": bool(description),
            "website": bool(website),
            "category": bool(category),
            "stage": bool(stage),
            "token_symbol": bool(token_symbol),
            "chain_focus": bool(chain_focus),
            "social_links": bool(social_links),
        }
        missing = [key for key, present in fields.items() if not present]
        score = sum(1 for present in fields.values() if present) / len(fields)
        return {
            "completeness_score": round(score, 4),
            "missing_fields": missing,
            "source_count": source_count,
        }

    def _url_name_score(self, url: str, name_token: str) -> int:
        parsed = urlparse(url)
        host = parsed.netloc.lower()
        path = parsed.path.lower()
        score = 0
        if name_token in host:
            score += 3
        if name_token in path:
            score += 2
        return score

    @staticmethod
    def _name_token(name: str | None) -> str | None:
        if not name:
            return None
        token = re.sub(r"[^a-z0-9]", "", name.lower())
        return token if len(token) >= 3 else None

    def _is_generic_name(self, value: str) -> bool:
        words = [w.lower() for w in value.split() if w]
        if not words:
            return True
        return all(word in self._GENERIC_NAME_WORDS for word in words)

    @staticmethod
    def _keyword_count(text: str, keyword: str) -> int:
        return len(re.findall(rf"\b{re.escape(keyword)}\b", text))

    @staticmethod
    def _split_sentences(text: str) -> list[str]:
        return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]

    @staticmethod
    def _clean_name(raw: str) -> str | None:
        normalized = re.sub(r"[^A-Za-z0-9\-\s]", " ", raw)
        normalized = re.sub(r"\s+", " ", normalized).strip()
        if not normalized:
            return None
        if "-" in normalized and " " not in normalized:
            normalized = normalized.replace("-", " ")
        words = [word.capitalize() for word in normalized.split(" ") if word]
        if not words:
            return None
        return " ".join(words[:4])

    @staticmethod
    def _is_url(value: str) -> bool:
        parsed = urlparse(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)

    @staticmethod
    def _host(url: str) -> str:
        return urlparse(url).netloc.lower()

    @staticmethod
    def _domain_label(url: str) -> str | None:
        host = urlparse(url).netloc.lower()
        host = host.removeprefix("www.")
        label = host.split(".")[0]
        if not label:
            return None
        return label.capitalize()
