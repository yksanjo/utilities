.PHONY: test clean install demo help

help:
	@echo "Available commands:"
	@echo "  make test     - Run all unit tests"
	@echo "  make demo     - Run demo of all utilities"
	@echo "  make clean    - Clean generated files"
	@echo "  make install  - Install dependencies"

test:
	python -m pytest tests/ -v

demo:
	@echo "=== Markdown to HTML Demo ==="
	cd markdown-to-html && python md2html.py example.md
	@echo ""
	@echo "=== Mini-Git Demo ==="
	cd mini-git && python minigit.py init
	@echo "test" > mini-git/test_demo.txt
	cd mini-git && python minigit.py add test_demo.txt
	cd mini-git && python minigit.py commit -m "Demo commit"
	cd mini-git && python minigit.py log
	cd mini-git && python minigit.py status
	@rm -f mini-git/test_demo.txt
	@echo ""
	@echo "=== TinyEdit ==="
	@echo "Run: cd tiny-editor && python tinyedit.py"

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	rm -f markdown-to-html/example.html
	rm -rf mini-git/.minigit

install:
	pip install pytest
