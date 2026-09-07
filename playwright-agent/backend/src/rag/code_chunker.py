"""
Structural Code Chunker for RAG Ingestion
==========================================
Chunks Python Playwright files structurally (by Page Object, Method, Fixture, Utility)
and attaches rich metadata required for metadata-filtered semantic retrieval.
"""

import ast
import os
from typing import Any, Dict, List, Optional


class CodeChunk:
    def __init__(
        self,
        chunk_id: str,
        document_id: str,
        content: str,
        metadata: Dict[str, Any]
    ):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.content = content
        self.metadata = metadata

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunkId": self.chunk_id,
            "documentId": self.document_id,
            "content": self.content,
            "metadata": self.metadata
        }


class StructuralCodeChunker:
    """
    Splits Python files by structural units (classes, functions, fixtures)
    rather than naive line/character count boundaries.
    """

    def __init__(self, root_dir: str):
        self.root_dir = os.path.abspath(root_dir)

    def chunk_file(self, file_path: str, doc_type: str) -> List[CodeChunk]:
        """Reads and chunks a Python file structurally."""
        if not os.path.exists(file_path):
            return []

        with open(file_path, "r", encoding="utf-8") as f:
            raw_source = f.read()

        rel_path = os.path.relpath(file_path, self.root_dir).replace("\\", "/")
        doc_id = os.path.splitext(os.path.basename(file_path))[0]
        chunks: List[CodeChunk] = []

        try:
            tree = ast.parse(raw_source, filename=file_path)
            lines = raw_source.splitlines()

            # Class definitions (Page Objects / Utilities)
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    class_name = node.name
                    class_lines = lines[node.lineno - 1 : node.end_lineno]
                    class_content = "\n".join(class_lines)

                    chunk_id = f"{doc_id}-{class_name}"
                    chunks.append(
                        CodeChunk(
                            chunk_id=chunk_id,
                            document_id=doc_id,
                            content=class_content,
                            metadata={
                                "project": "playwright",
                                "documentType": doc_type,
                                "filePath": rel_path,
                                "language": "python",
                                "framework": "playwright",
                                "version": "1.0",
                                "module": doc_id,
                                "symbolName": class_name,
                                "isClass": True
                            }
                        )
                    )

                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func_name = node.name
                    func_lines = lines[node.lineno - 1 : node.end_lineno]
                    func_content = "\n".join(func_lines)

                    is_fixture = any(
                        (isinstance(d, ast.Attribute) and d.attr == "fixture") or
                        (isinstance(d, ast.Call) and getattr(d.func, "attr", "") == "fixture")
                        for d in node.decorator_list
                    )
                    actual_type = "fixture" if is_fixture else doc_type

                    chunk_id = f"{doc_id}-{func_name}"
                    chunks.append(
                        CodeChunk(
                            chunk_id=chunk_id,
                            document_id=doc_id,
                            content=func_content,
                            metadata={
                                "project": "playwright",
                                "documentType": actual_type,
                                "filePath": rel_path,
                                "language": "python",
                                "framework": "playwright",
                                "version": "1.0",
                                "module": doc_id,
                                "symbolName": func_name,
                                "isFixture": is_fixture
                            }
                        )
                    )

            # Fallback if no structural classes/functions found or file is small config/module
            if not chunks:
                chunks.append(
                    CodeChunk(
                        chunk_id=f"{doc_id}-full",
                        document_id=doc_id,
                        content=raw_source,
                        metadata={
                            "project": "playwright",
                            "documentType": doc_type,
                            "filePath": rel_path,
                            "language": "python",
                            "framework": "playwright",
                            "version": "1.0",
                            "module": doc_id,
                            "symbolName": doc_id
                        }
                    )
                )

        except Exception as e:
            # Fallback on syntax/parse errors
            chunks.append(
                CodeChunk(
                    chunk_id=f"{doc_id}-fallback",
                    document_id=doc_id,
                    content=raw_source,
                    metadata={
                        "project": "playwright",
                        "documentType": doc_type,
                        "filePath": rel_path,
                        "language": "python",
                        "framework": "playwright",
                        "version": "1.0",
                        "module": doc_id,
                        "symbolName": doc_id,
                        "parseError": str(e)
                    }
                )
            )

        return chunks
