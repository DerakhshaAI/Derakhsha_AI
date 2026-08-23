"""
درخشا · معماری هوش مصنوعی مغز‌محور
نسخه ۰.۸ با قابلیت مدیریت اسناد (Document Cortex)
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
import json
import random
from datetime import datetime


# =========================== کلاس‌های پایه ===========================

class Cortex(ABC):
    """قشر پایه – همه قشرها از این ارث‌بری می‌کنند."""
    
    def __init__(self, name: str):
        self.name = name
        self.active = False
        self.log = []

    @abstractmethod
    def process(self, data: Any) -> Any:
        pass

    def activate(self):
        self.active = True
        self.log.append(f"{self.name} فعال شد")

    def deactivate(self):
        self.active = False
        self.log.append(f"{self.name} غیرفعال شد")


class KnowledgeNode:
    """گره درخت دانش – شامل نام، فرزندان، وزن، و داده‌های زمانی/احتمالاتی."""
    
    def __init__(self, name: str, parent: Optional[KnowledgeNode] = None):
        self.name = name
        self.parent = parent
        self.children: List[KnowledgeNode] = []
        self.weight = 1.0
        self.confidence = 0.5
        self.temporal_series: List[float] = []
        self.metadata: Dict[str, Any] = {}
        self.documents: List[Document] = []  # اسناد متصل به این گره

    def add_child(self, child: KnowledgeNode):
        child.parent = self
        self.children.append(child)

    def find(self, name: str) -> Optional[KnowledgeNode]:
        if self.name == name:
            return self
        for ch in self.children:
            result = ch.find(name)
            if result:
                return result
        return None

    def path_from_root(self) -> List[str]:
        path = []
        node = self
        while node:
            path.append(node.name)
            node = node.parent
        return path[::-1]

    def descendants(self) -> List[KnowledgeNode]:
        result = [self]
        for ch in self.children:
            result.extend(ch.descendants())
        return result

    def attach_document(self, doc: Document):
        """اتصال یک سند به این گره."""
        if doc not in self.documents:
            self.documents.append(doc)
            doc.related_nodes.append(self)


class KnowledgeForest:
    """جنگل دانش – مجموعه‌ای از درخت‌های تخصصی."""
    
    def __init__(self):
        self.trees: List[KnowledgeNode] = []

    def add_tree(self, root: KnowledgeNode):
        self.trees.append(root)

    def find_global(self, name: str) -> Optional[KnowledgeNode]:
        for tree in self.trees:
            found = tree.find(name)
            if found:
                return found
        return None

    def connect_concepts(self, name1: str, name2: str, relation: str):
        node1 = self.find_global(name1)
        node2 = self.find_global(name2)
        if node1 and node2:
            node1.metadata[relation] = node2.name
            node2.metadata[relation] = node1.name
            return True
        return False


# =========================== کلاس سند ===========================

class Document:
    """نماینده یک سند (مقاله، کتاب، یادداشت)."""
    
    def __init__(self, title: str, content: str, subject: str, keywords: List[str]):
        self.title = title
        self.content = content
        self.subject = subject
        self.keywords = keywords
        self.date_added = datetime.now().isoformat()
        self.related_nodes: List[KnowledgeNode] = []

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "content": self.content[:200] + "...",
            "subject": self.subject,
            "keywords": self.keywords,
            "date": self.date_added,
            "related_nodes": [n.name for n in self.related_nodes]
        }


# =========================== قشر اسناد (جدید) ===========================

class DocumentCortex(Cortex):
    """مدیریت و جستجوی اسناد متنی."""
    
    def __init__(self, forest: KnowledgeForest):
        super().__init__("DocumentCortex")
        self.forest = forest
        self.documents: List[Document] = []

    def add_document(self, title: str, content: str, subject: str, keywords: List[str], 
                     attach_to_nodes: Optional[List[str]] = None) -> Document:
        """افزودن سند جدید و اتصال به گره‌های دانش (در صورت وجود)."""
        if not self.active:
            self.log.append("قشر اسناد غیرفعال است، سند ذخیره نشد.")
            return None

        doc = Document(title, content, subject, keywords)
        self.documents.append(doc)
        self.log.append(f"سند '{title}' با موضوع '{subject}' افزوده شد.")

        # اتصال به گره‌های دانش
        if attach_to_nodes:
            for node_name in attach_to_nodes:
                node = self.forest.find_global(node_name)
                if node:
                    node.attach_document(doc)
                    self.log.append(f"سند به گره '{node_name}' متصل شد.")
                else:
                    self.log.append(f"گره '{node_name}' یافت نشد، اتصال انجام نشد.")
        return doc

    def search_by_keyword(self, query: str) -> List[Document]:
        """جستجوی اسناد بر اساس کلیدواژه، موضوع یا عنوان."""
        if not self.active:
            return []
        results = []
        query_lower = query.lower()
        for doc in self.documents:
            if (query_lower in doc.title.lower() or
                query_lower in doc.subject.lower() or
                any(query_lower in kw.lower() for kw in doc.keywords) or
                query_lower in doc.content.lower()):
                results.append(doc)
        self.log.append(f"جستجوی '{query}' → {len(results)} سند یافت شد.")
        return results

    def get_documents_for_node(self, node_name: str) -> List[Document]:
        """دریافت اسناد متصل به یک گره خاص."""
        node = self.forest.find_global(node_name)
        if node:
            return node.documents
        return []

    def get_all_documents(self) -> List[Document]:
        return self.documents


# =========================== سایر قشرها (خلاصه) ===========================

class InputCortex(Cortex):
    def __init__(self):
        super().__init__("InputCortex")
    def process(self, data: str) -> str:
        if not self.active:
            return data
        cleaned = data.strip().lower()
        cleaned = ' '.join(cleaned.split())
        self.log.append(f"متن ورودی: '{data}' → '{cleaned}'")
        return cleaned


class LanguageTreeCortex(Cortex):
    def __init__(self):
        super().__init__("LanguageTreeCortex")
        self.tree_cache = {}
    def process(self, sentence: str) -> Dict:
        if not self.active:
            return {"sentence": sentence, "tree": []}
        words = sentence.split()
        root = KnowledgeNode("جمله")
        for w in words:
            root.add_child(KnowledgeNode(w))
        self.tree_cache[sentence] = root
        self.log.append(f"درخت زبان برای '{sentence}' ساخته شد.")
        return {"sentence": sentence, "tree": root}


class KnowledgeForestCortex(Cortex):
    def __init__(self):
        super().__init__("KnowledgeForestCortex")
        self.forest = KnowledgeForest()
    def process(self, query: str) -> Optional[KnowledgeNode]:
        if not self.active:
            return None
        result = self.forest.find_global(query)
        self.log.append(f"جستجوی '{query}' در جنگل → {result.name if result else 'یافت نشد'}")
        return result


class SearchCortex(Cortex):
    def __init__(self, forest_cortex: KnowledgeForestCortex):
        super().__init__("SearchCortex")
        self.forest_cortex = forest_cortex
    def pyramid_search(self, concept: str) -> List[str]:
        if not self.active:
            return []
        node = self.forest_cortex.forest.find_global(concept)
        if node:
            path = node.path_from_root()
            self.log.append(f"جستجوی هرمی '{concept}' → {path}")
            return path
        return []
    def tree_search(self, root_concept: str, depth: int = 2) -> List[str]:
        if not self.active:
            return []
        node = self.forest_cortex.forest.find_global(root_concept)
        if node:
            result = []
            def collect(n, d):
                if d == 0:
                    return
                for ch in n.children:
                    result.append(ch.name)
                    collect(ch, d-1)
            collect(node, depth)
            self.log.append(f"جستجوی درختی '{root_concept}' (عمق {depth}) → {result}")
            return result
        return []


class ReasoningCortex(Cortex):
    def __init__(self):
        super().__init__("ReasoningCortex")
    def process(self, path: List[str]) -> bool:
        if not self.active:
            return True
        valid = len(path) > 0
        self.log.append(f"اعتبارسنجی مسیر {path} → {valid}")
        return valid


class LearningCortex(Cortex):
    def __init__(self):
        super().__init__("LearningCortex")
        self.history: Dict[str, float] = {}
    def process(self, path: List[str], success: bool) -> None:
        if not self.active:
            return
        key = "→".join(path)
        if success:
            self.history[key] = self.history.get(key, 0.0) + 0.1
        else:
            self.history[key] = self.history.get(key, 0.0) - 0.1
        self.log.append(f"یادگیری: {key} → امتیاز {self.history[key]:.2f}")


class TreeNeuronCortex(Cortex):
    def __init__(self, forest_cortex: KnowledgeForestCortex):
        super().__init__("TreeNeuronCortex")
        self.forest_cortex = forest_cortex
    def process(self, root_name: str) -> Dict:
        if not self.active:
            return {}
        root = self.forest_cortex.forest.find_global(root_name)
        if not root:
            return {}
        count = len(root.descendants())
        self.log.append(f"Tree-Neuron '{root_name}' شامل {count} گره")
        return {"root": root_name, "node_count": count}


class MonitorCortex(Cortex):
    def __init__(self):
        super().__init__("MonitorCortex")
        self.color_map = {}
    def process(self, path: List[str]) -> str:
        if not self.active:
            return "مونیتور غیرفعال"
        for node in path:
            self.color_map[node] = f"#{random.randint(0, 0xFFFFFF):06x}"
        self.log.append(f"رنگ‌ها برای مسیر {path} اختصاص یافت")
        return " | ".join([f"{n} ({self.color_map.get(n, '#fff')})" for n in path])


# =========================== قشرهای جدید ===========================

class TemporalCortex(Cortex):
    def __init__(self):
        super().__init__("TemporalCortex")
        self.sequence_db: Dict[str, List[float]] = {}
    def process(self, node: KnowledgeNode, new_value: float) -> None:
        if not self.active:
            return
        node.temporal_series.append(new_value)
        self.sequence_db[node.name] = node.temporal_series
        self.log.append(f"زمان‌بندی برای '{node.name}': افزودن {new_value}")
    def predict(self, node: KnowledgeNode, steps: int = 3) -> List[float]:
        if not self.active or not node.temporal_series:
            return []
        series = node.temporal_series
        avg = sum(series) / len(series)
        prediction = [avg + random.uniform(-0.5, 0.5) for _ in range(steps)]
        self.log.append(f"پیش‌بینی برای '{node.name}': {prediction}")
        return prediction


class StochasticCortex(Cortex):
    def __init__(self):
        super().__init__("StochasticCortex")
    def process(self, query: str, forest: KnowledgeForest) -> List[Tuple[KnowledgeNode, float]]:
        if not self.active:
            return []
        results = []
        for tree in forest.trees:
            node = tree.find(query)
            if node:
                node.confidence = min(1.0, node.confidence + random.uniform(0, 0.3))
                results.append((node, node.confidence))
        self.log.append(f"جستجوی احتمالاتی '{query}' → {len(results)} نتیجه")
        return sorted(results, key=lambda x: x[1], reverse=True)


class PruningCortex(Cortex):
    def __init__(self):
        super().__init__("PruningCortex")
        self.active_memory: List[KnowledgeNode] = []
    def prune(self, node: KnowledgeNode, threshold: float = 0.2) -> None:
        if not self.active:
            return
        to_remove = [ch for ch in node.children if ch.weight < threshold]
        for ch in to_remove:
            node.children.remove(ch)
            self.log.append(f"هرس: {ch.name} حذف شد (وزن {ch.weight:.2f})")
    def graft(self, parent: KnowledgeNode, child: KnowledgeNode) -> None:
        if not self.active:
            return
        parent.add_child(child)
        self.log.append(f"پیوند: {child.name} به {parent.name} متصل شد")


class MetaCognitionCortex(Cortex):
    def __init__(self):
        super().__init__("MetaCognitionCortex")
        self.strategy = "pyramid"
    def process(self, context: Dict) -> str:
        if not self.active:
            return self.strategy
        if context.get("response_time", 0) > 2.0:
            self.strategy = "tree" if self.strategy == "pyramid" else "pyramid"
            self.log.append(f"تغییر استراتژی به {self.strategy}")
        else:
            self.log.append(f"استراتژی فعلی: {self.strategy}")
        return self.strategy


class AnalogicalReasoningCortex(Cortex):
    def __init__(self):
        super().__init__("AnalogicalReasoningCortex")
    def process(self, source_pattern: List[str], target_domain: KnowledgeNode) -> List[str]:
        if not self.active:
            return []
        analogies = []
        for node in target_domain.descendants():
            for word in source_pattern:
                if word in node.name or node.name in word:
                    analogies.append(node.name)
        self.log.append(f"قیاس از {source_pattern} به {target_domain.name} → {analogies}")
        return analogies


# =========================== کلاس اصلی درخشا ===========================

class Drakhsha:
    """سیستم اصلی درخشا – تمام قشرها را هماهنگ می‌کند."""
    
    def __init__(self):
        self.input_cortex = InputCortex()
        self.language_cortex = LanguageTreeCortex()
        self.forest_cortex = KnowledgeForestCortex()
        self.search_cortex = SearchCortex(self.forest_cortex)
        self.reasoning_cortex = ReasoningCortex()
        self.learning_cortex = LearningCortex()
        self.tree_neuron_cortex = TreeNeuronCortex(self.forest_cortex)
        self.monitor_cortex = MonitorCortex()
        self.temporal_cortex = TemporalCortex()
        self.stochastic_cortex = StochasticCortex()
        self.pruning_cortex = PruningCortex()
        self.meta_cognition_cortex = MetaCognitionCortex()
        self.analogical_cortex = AnalogicalReasoningCortex()

        # قشر جدید اسناد
        self.document_cortex = DocumentCortex(self.forest_cortex.forest)

        self._init_sample_forest()

        # فعال‌سازی پیش‌فرض
        self.input_cortex.activate()
        self.forest_cortex.activate()
        self.search_cortex.activate()
        self.reasoning_cortex.activate()
        self.document_cortex.activate()   # فعال کردن قشر اسناد

    def _init_sample_forest(self):
        bio = KnowledgeNode("زیست‌شناسی")
        cell = KnowledgeNode("سلول")
        cell.add_child(KnowledgeNode("هسته"))
        cell.add_child(KnowledgeNode("میتوکندری"))
        cell.add_child(KnowledgeNode("کلروپلاست"))
        bio.add_child(cell)
        bio.add_child(KnowledgeNode("قلب"))
        bio.add_child(KnowledgeNode("فتوسنتز"))

        phys = KnowledgeNode("فیزیک")
        mech = KnowledgeNode("مکانیک")
        mech.add_child(KnowledgeNode("قوانین نیوتن"))
        mech.add_child(KnowledgeNode("کار و انرژی"))
        phys.add_child(mech)
        phys.add_child(KnowledgeNode("نور"))

        tech = KnowledgeNode("فناوری")
        ai = KnowledgeNode("هوش مصنوعی")
        ai.add_child(KnowledgeNode("یادگیری عمیق"))
        ai.add_child(KnowledgeNode("درخت تصمیم"))
        tech.add_child(ai)
        tech.add_child(KnowledgeNode("شبکه"))

        self.forest_cortex.forest.add_tree(bio)
        self.forest_cortex.forest.add_tree(phys)
        self.forest_cortex.forest.add_tree(tech)

    def add_document(self, title: str, content: str, subject: str, keywords: List[str], 
                     attach_to: Optional[List[str]] = None) -> Optional[Document]:
        """رابطه عمومی برای افزودن سند."""
        return self.document_cortex.add_document(title, content, subject, keywords, attach_to)

    def search_documents(self, query: str) -> List[Document]:
        """جستجوی اسناد."""
        return self.document_cortex.search_by_keyword(query)

    def process_query(self, query: str) -> Dict:
        """پردازش یک پرسش (همراه با جستجوی اسناد)."""
        cleaned = self.input_cortex.process(query)
        lang_tree = self.language_cortex.process(cleaned)
        found_node = self.forest_cortex.process(cleaned)

        path = []
        valid = False
        if found_node:
            path = found_node.path_from_root()
            valid = self.reasoning_cortex.process(path)

        self.learning_cortex.process(path, valid)

        # جستجوی اسناد مرتبط
        related_docs = self.document_cortex.search_by_keyword(cleaned)

        result = {
            "query": query,
            "cleaned": cleaned,
            "found": found_node.name if found_node else None,
            "path": path,
            "valid": valid,
            "lang_tree": lang_tree,
            "related_documents": [doc.to_dict() for doc in related_docs]
        }

        # فعال‌سازی قشرهای جدید در صورت نیاز
        if found_node:
            self.temporal_cortex.process(found_node, random.uniform(0, 10))
            self.stochastic_cortex.process(cleaned, self.forest_cortex.forest)
            self.meta_cognition_cortex.process({"response_time": random.uniform(0.5, 3)})
            if path:
                target = self.forest_cortex.forest.find_global("فناوری")
                if target:
                    analogies = self.analogical_cortex.process(path, target)
                    result["analogies"] = analogies

        return result

    def get_logs(self) -> Dict[str, List[str]]:
        return {
            "input": self.input_cortex.log,
            "language": self.language_cortex.log,
            "forest": self.forest_cortex.log,
            "search": self.search_cortex.log,
            "reasoning": self.reasoning_cortex.log,
            "learning": self.learning_cortex.log,
            "tree_neuron": self.tree_neuron_cortex.log,
            "monitor": self.monitor_cortex.log,
            "temporal": self.temporal_cortex.log,
            "stochastic": self.stochastic_cortex.log,
            "pruning": self.pruning_cortex.log,
            "meta": self.meta_cognition_cortex.log,
            "analogical": self.analogical_cortex.log,
            "document": self.document_cortex.log,
        }


# =========================== اجرای نمونه ===========================

if __name__ == "__main__":
    drakhsha = Drakhsha()

    # افزودن یک سند نمونه
    drakhsha.add_document(
        title="مبانی یادگیری عمیق",
        content="یادگیری عمیق شاخه‌ای از یادگیری ماشین است که از شبکه‌های عصبی چندلایه استفاده می‌کند...",
        subject="هوش مصنوعی",
        keywords=["یادگیری عمیق", "شبکه عصبی", "پردازش"],
        attach_to=["هوش مصنوعی", "یادگیری عمیق"]
    )

    # پردازش یک پرسش
    print("🔍 درخشا در حال پردازش...")
    result = drakhsha.process_query("یادگیری عمیق")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # جستجوی اسناد
    print("\n📄 جستجوی اسناد برای 'هوش مصنوعی':")
    docs = drakhsha.search_documents("هوش مصنوعی")
    for d in docs:
        print(f"  - {d.title} (موضوع: {d.subject})")

    print("\n📋 لاگ قشر اسناد:")
    logs = drakhsha.get_logs()
    for log in logs["document"]:
        print(f"  {log}")
