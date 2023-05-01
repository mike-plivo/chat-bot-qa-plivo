from typing import Any, Callable, List, Optional
from langchain.schema import Document
from langchain.document_loaders.sitemap import SitemapLoader


class SitemapChunkLoader(SitemapLoader):
    def __init__(
        self,
        web_path: str,
        filter_urls: Optional[List[str]] = None,
        parsing_function: Optional[Callable] = None,
    ):
        super().__init__(web_path, filter_urls, parsing_function)
        self._els = None

    def load_chunks(self, chunk_size=200) -> List[Document]:
        """Load sitemap in chunks."""
        if self._els is None:
            print("Loading sitemap")
            soup = self.scrape("xml")
            self._els = self.parse_sitemap(soup)

        if len(self._els) <= 0:
            print("No more documents to load")
            return []

        print(f"Loading {chunk_size} documents from sitemap")
        els = []
        els = self._els[:chunk_size]
        self._els = self._els[chunk_size:]
        print(f"Found {len(els)} documents to load from sitemap")

        results = []
        for el in els:
            if "loc" not in el:
                print(f"Skipping {el} because it has no loc")
                continue
            url = el["loc"].strip()
            print(f"Loading {url}")
            data = self._scrape(url)
            results.append((url, data, el))

        print(f"Loaded {len(results)} documents from sitemap")
        return [
            Document(
                page_content=self.parsing_function(data),
                metadata={**{"source": url}, **el},
            )
            for url, data, metadata in results
        ]

