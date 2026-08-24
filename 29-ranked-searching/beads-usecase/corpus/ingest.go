package corpus

import (
	"bufio"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"net/url"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strings"

	"verifiedskiplist/beads-usecase/model"
)

var (
	mdRefDef = regexp.MustCompile(`(?m)^\s*\[([^\]]+)\]:\s*<?([^\s>]+)>?`)
	htmlHref = regexp.MustCompile(`(?is)<a\b[^>]*?href\s*=\s*["']([^"']+)["'][^>]*>(.*?)</a>`)
	htmlTags = regexp.MustCompile(`<[^>]+>`)
)

const sourceRepo = "https://github.com/gastownhall/beads"

type IngestOptions struct {
	ProjectID string
	SourceRef string
	Redirects map[string]string
}

// IngestRepo converts every Markdown file in a Beads checkout into the PoC
// Memory projection and returns a lossless citation table alongside it. The
// broad repo corpus is intentional: graph-shape experiments need isolates and
// the long tail, not only the hand-selected documentation navigation set.
func IngestRepo(root string) ([]model.Memory, []model.Citation, error) {
	return IngestRepoAt(root, "")
}

func IngestRepoAt(root, sourceRef string) ([]model.Memory, []model.Citation, error) {
	paths, err := markdownPaths(root)
	if err != nil {
		return nil, nil, err
	}
	return ingestPaths(paths, root, IngestOptions{ProjectID: "beads-public-repo", SourceRef: sourceRef})
}

// IngestDocs preserves the earlier docs-only entry point for focused tests.
func IngestDocs(root string) ([]model.Memory, error) {
	return IngestDocsAt(root, "")
}

func IngestDocsAt(root, sourceRef string) ([]model.Memory, error) {
	m, _, err := IngestDocsGraphAt(root, sourceRef)
	return m, err
}

// IngestDocsGraphAt imports every Markdown document under root and preserves
// the raw authored hyperlink occurrences as well as unique Memory references.
func IngestDocsGraphAt(root, sourceRef string) ([]model.Memory, []model.Citation, error) {
	repoRoot := root
	if filepath.Base(filepath.Clean(root)) == "docs" {
		repoRoot = filepath.Dir(filepath.Clean(root))
	}
	paths, err := markdownPaths(root)
	if err != nil {
		return nil, nil, err
	}
	return ingestPaths(paths, repoRoot, IngestOptions{ProjectID: "beads-docs", SourceRef: sourceRef})
}

func ingestPaths(paths []string, repoRoot string, opt IngestOptions) ([]model.Memory, []model.Citation, error) {
	if opt.ProjectID == "" {
		opt.ProjectID = "beads-import"
	}
	paths = append([]string(nil), paths...)
	sort.Strings(paths)
	known := make(map[string]string, len(paths))
	for _, p := range paths {
		rel, err := filepath.Rel(repoRoot, p)
		if err != nil {
			return nil, nil, err
		}
		rel = filepath.ToSlash(rel)
		known[cleanDocPath(rel)] = memoryID(rel)
	}

	mem := make([]model.Memory, 0, len(paths))
	var citations []model.Citation
	for _, p := range paths {
		b, err := os.ReadFile(p)
		if err != nil {
			return nil, nil, err
		}
		rel, err := filepath.Rel(repoRoot, p)
		if err != nil {
			return nil, nil, err
		}
		rel = filepath.ToSlash(rel)
		title, _, body := frontmatter(string(b))
		if title == "" {
			title = firstHeading(string(b))
		}
		if title == "" {
			title = strings.TrimSuffix(filepath.Base(rel), filepath.Ext(rel))
		}
		refs, cites := references(rel, string(b), known, opt.Redirects)
		citations = append(citations, cites...)
		h := sha256.Sum256(b)
		mem = append(mem, model.Memory{
			ID: memoryID(rel), ProjectID: opt.ProjectID, Title: title, Body: body,
			Key: cleanDocPath(rel), References: refs,
			Provenance: model.Provenance{
				Kind:       "imported-documentation",
				SourcePath: rel,
				SourceURL:  sourceURL(opt.SourceRef, rel),
				SourceSHA:  hex.EncodeToString(h[:]),
				SourceType: sourceType(rel),
				SourceRepo: sourceRepo,
				SourceRef:  opt.SourceRef,
			},
		})
	}
	return mem, citations, nil
}

func markdownPaths(root string) ([]string, error) {
	var paths []string
	err := filepath.WalkDir(root, func(path string, d os.DirEntry, err error) error {
		if err != nil {
			return err
		}
		if d.IsDir() {
			if d.Name() == ".git" || d.Name() == "node_modules" || d.Name() == "vendor" {
				return filepath.SkipDir
			}
			return nil
		}
		ext := strings.ToLower(filepath.Ext(path))
		if ext == ".md" || ext == ".mdx" || ext == ".markdown" {
			paths = append(paths, path)
		}
		return nil
	})
	sort.Strings(paths)
	return paths, err
}

func memoryID(rel string) string {
	return "mem:repo/" + cleanDocPath(rel)
}

func cleanDocPath(rel string) string {
	rel = filepath.ToSlash(filepath.Clean(rel))
	rel = strings.TrimPrefix(rel, "./")
	for _, ext := range []string{".markdown", ".mdx", ".md"} {
		if strings.HasSuffix(strings.ToLower(rel), ext) {
			rel = rel[:len(rel)-len(ext)]
			break
		}
	}
	return strings.TrimSuffix(rel, "/")
}

func sourceType(rel string) string {
	rel = filepath.ToSlash(rel)
	switch {
	case strings.HasPrefix(rel, "docs/cli-reference/") || rel == "docs/CLI_REFERENCE.md":
		return "generated-cli-doc"
	case strings.HasPrefix(rel, "docs/"):
		return "site-doc"
	case strings.HasPrefix(rel, "engdocs/"):
		return "engineering-doc"
	case strings.HasPrefix(rel, ".claude/") || strings.HasPrefix(rel, ".agent/") || strings.HasPrefix(rel, ".github/"):
		return "agent-or-project-guidance"
	case strings.HasPrefix(rel, "plugins/"):
		return "plugin-doc"
	case strings.HasPrefix(rel, "examples/") || strings.HasPrefix(rel, "integrations/"):
		return "example-or-integration-doc"
	case strings.HasPrefix(filepath.Base(rel), "PROPOSAL-"):
		return "proposal"
	case !strings.Contains(rel, "/"):
		return "root-doc"
	default:
		return "other-markdown"
	}
}

func frontmatter(s string) (title, desc, body string) {
	if !strings.HasPrefix(s, "---\n") {
		return "", "", s
	}
	sc := bufio.NewScanner(strings.NewReader(s))
	sc.Scan()
	for sc.Scan() {
		line := sc.Text()
		if line == "---" {
			break
		}
		if k, v, ok := strings.Cut(line, ":"); ok {
			v = strings.Trim(strings.TrimSpace(v), `"'`)
			switch strings.TrimSpace(k) {
			case "title":
				title = v
			case "description":
				desc = v
			}
		}
	}
	var rest []string
	for sc.Scan() {
		rest = append(rest, sc.Text())
	}
	return title, desc, strings.Join(rest, "\n")
}

func firstHeading(s string) string {
	for _, line := range strings.Split(s, "\n") {
		line = strings.TrimSpace(line)
		if strings.HasPrefix(line, "# ") {
			return strings.TrimSpace(strings.TrimPrefix(line, "# "))
		}
	}
	return ""
}

type linkOccurrence struct {
	anchor string
	target string
	syntax string
	pos    int
}

func references(rel, source string, known map[string]string, redirects map[string]string) ([]model.Reference, []model.Citation) {
	masked := maskMarkdownCode(source)
	defs := referenceDefinitions(masked)
	occ := extractMarkdownLinks(masked, source, defs)
	for _, m := range htmlHref.FindAllStringSubmatchIndex(masked, -1) {
		if len(m) < 6 {
			continue
		}
		target := source[m[2]:m[3]]
		anchor := htmlTags.ReplaceAllString(source[m[4]:m[5]], "")
		occ = append(occ, linkOccurrence{anchor: strings.TrimSpace(anchor), target: strings.TrimSpace(target), syntax: "html", pos: m[0]})
	}
	sort.SliceStable(occ, func(i, j int) bool { return occ[i].pos < occ[j].pos })

	seenEdge := map[string]bool{}
	var refs []model.Reference
	cites := make([]model.Citation, 0, len(occ))
	for _, o := range occ {
		target := strings.TrimSpace(o.target)
		if target == "" {
			continue
		}
		resolvedPath, targetID, fragment, internal, host, class := resolveTarget(rel, target, known, redirects)
		c := model.Citation{
			SourceID: memoryID(rel), SourcePath: rel, SourceLine: lineAt(source, o.pos),
			AnchorText: strings.TrimSpace(o.anchor), RawTarget: target,
			TargetID: targetID, TargetPath: resolvedPath, Fragment: fragment,
			Syntax: o.syntax, Class: class, Internal: internal, Resolved: targetID != "", ExternalHost: host,
		}
		cites = append(cites, c)
		if targetID != "" && !seenEdge[targetID] && targetID != memoryID(rel) {
			seenEdge[targetID] = true
			refs = append(refs, model.Reference{TargetID: targetID, Kind: "imported-doc-link"})
		}
	}
	return refs, cites
}

func referenceDefinitions(masked string) map[string]string {
	defs := map[string]string{}
	for _, m := range mdRefDef.FindAllStringSubmatch(masked, -1) {
		if len(m) >= 3 {
			defs[strings.ToLower(strings.TrimSpace(m[1]))] = strings.TrimSpace(m[2])
		}
	}
	return defs
}

// extractMarkdownLinks recognizes inline links and reference-style links while
// deliberately excluding images and fenced/inline code. It does not attempt to
// interpret arbitrary Markdown extensions; every unresolved occurrence remains
// auditable in the Citation table rather than being silently invented.
func extractMarkdownLinks(masked, original string, defs map[string]string) []linkOccurrence {
	var out []linkOccurrence
	for i := 0; i < len(masked); i++ {
		if masked[i] != '[' || (i > 0 && masked[i-1] == '!') {
			continue
		}
		close := findUnescaped(masked, ']', i+1)
		if close < 0 {
			continue
		}
		anchor := original[i+1 : close]
		// A reference definition, [name]: target, declares a destination but is
		// not itself a citation occurrence. Only a later [label][name] (or
		// shortcut [name]) creates an edge-side record.
		if isReferenceDefinitionAt(masked, i, close) {
			i = close
			continue
		}
		// Inline: [label](target "optional title")
		if close+1 < len(masked) && masked[close+1] == '(' {
			end := findClosingParen(masked, close+2)
			if end < 0 {
				continue
			}
			target := markdownDestination(original[close+2 : end])
			if target != "" {
				out = append(out, linkOccurrence{anchor: anchor, target: target, syntax: "markdown-inline", pos: i})
			}
			i = end
			continue
		}
		// Full/collapsed reference: [label][ref], [label][]
		if close+1 < len(masked) && masked[close+1] == '[' {
			end := findUnescaped(masked, ']', close+2)
			if end < 0 {
				continue
			}
			key := strings.TrimSpace(original[close+2 : end])
			if key == "" {
				key = anchor
			}
			if target, ok := defs[strings.ToLower(strings.TrimSpace(key))]; ok {
				out = append(out, linkOccurrence{anchor: anchor, target: target, syntax: "markdown-reference", pos: i})
			}
			i = end
			continue
		}
		// Shortcut reference: [ref] only when a matching definition exists.
		if target, ok := defs[strings.ToLower(strings.TrimSpace(anchor))]; ok {
			out = append(out, linkOccurrence{anchor: anchor, target: target, syntax: "markdown-reference", pos: i})
		}
	}
	return out
}

func isReferenceDefinitionAt(s string, open, close int) bool {
	lineStart := strings.LastIndex(s[:open], "\n") + 1
	if strings.TrimSpace(s[lineStart:open]) != "" {
		return false
	}
	i := close + 1
	for i < len(s) && (s[i] == ' ' || s[i] == '\t') {
		i++
	}
	return i < len(s) && s[i] == ':'
}

func findUnescaped(s string, want byte, start int) int {
	for i := start; i < len(s); i++ {
		if s[i] == want && (i == 0 || s[i-1] != '\\') {
			return i
		}
	}
	return -1
}

func findClosingParen(s string, start int) int {
	depth := 1
	angle := false
	for i := start; i < len(s); i++ {
		if i > start && s[i-1] == '\\' {
			continue
		}
		switch s[i] {
		case '<':
			angle = true
		case '>':
			angle = false
		case '(':
			if !angle {
				depth++
			}
		case ')':
			if !angle {
				depth--
				if depth == 0 {
					return i
				}
			}
		}
	}
	return -1
}

func markdownDestination(s string) string {
	s = strings.TrimSpace(s)
	if s == "" {
		return ""
	}
	if strings.HasPrefix(s, "<") {
		if j := strings.IndexByte(s, '>'); j >= 0 {
			return strings.TrimSpace(s[1:j])
		}
	}
	for i, r := range s {
		if r == ' ' || r == '\t' || r == '\n' || r == '\r' {
			return strings.TrimSpace(s[:i])
		}
	}
	return s
}

func maskMarkdownCode(s string) string {
	b := []byte(s)
	inFence := false
	fence := ""
	lineStart := 0
	for lineStart < len(b) {
		lineEnd := lineStart
		for lineEnd < len(b) && b[lineEnd] != '\n' {
			lineEnd++
		}
		line := strings.TrimSpace(string(b[lineStart:lineEnd]))
		marker := ""
		if strings.HasPrefix(line, "```") {
			marker = "```"
		} else if strings.HasPrefix(line, "~~~") {
			marker = "~~~"
		}
		if marker != "" {
			if !inFence {
				inFence, fence = true, marker
			} else if marker == fence {
				inFence, fence = false, ""
			}
			for i := lineStart; i < lineEnd; i++ {
				b[i] = ' '
			}
		} else if inFence {
			for i := lineStart; i < lineEnd; i++ {
				b[i] = ' '
			}
		} else {
			// Mask inline-code spans. This intentionally treats each backtick run
			// as a delimiter of the same length; malformed spans remain visible.
			for i := lineStart; i < lineEnd; {
				if b[i] != '`' {
					i++
					continue
				}
				n := 1
				for i+n < lineEnd && b[i+n] == '`' {
					n++
				}
				close := -1
				for j := i + n; j+n <= lineEnd; j++ {
					ok := true
					for k := 0; k < n; k++ {
						if b[j+k] != '`' {
							ok = false
							break
						}
					}
					if ok {
						close = j
						break
					}
				}
				if close < 0 {
					i += n
					continue
				}
				for j := i; j < close+n; j++ {
					b[j] = ' '
				}
				i = close + n
			}
		}
		lineStart = lineEnd + 1
	}
	return string(b)
}

func lineAt(s string, pos int) int {
	if pos <= 0 {
		return 1
	}
	if pos > len(s) {
		pos = len(s)
	}
	return 1 + strings.Count(s[:pos], "\n")
}

func resolveTarget(sourceRel, raw string, known map[string]string, redirects map[string]string) (path, id, fragment string, internal bool, host, class string) {
	t := strings.TrimSpace(strings.Trim(raw, "<>"))
	if strings.HasPrefix(t, "#") {
		return cleanDocPath(sourceRel), memoryID(sourceRel), t, true, "", "local-fragment"
	}
	if u, err := url.Parse(t); err == nil && u.Scheme != "" {
		host = strings.ToLower(u.Hostname())
		if strings.EqualFold(u.Scheme, "mailto") || strings.EqualFold(u.Scheme, "tel") {
			return "", "", u.Fragment, false, host, "external"
		}
		fragment = fragmentValue(u.Fragment)
		switch host {
		case "github.com":
			parts := strings.Split(strings.TrimPrefix(u.Path, "/"), "/")
			if len(parts) >= 5 && parts[0] == "gastownhall" && parts[1] == "beads" && (parts[2] == "blob" || parts[2] == "tree") {
				t = strings.Join(parts[4:], "/")
				internal = true
			} else {
				return "", "", fragment, false, host, "external"
			}
		case "raw.githubusercontent.com":
			parts := strings.Split(strings.TrimPrefix(u.Path, "/"), "/")
			if len(parts) >= 4 && parts[0] == "gastownhall" && parts[1] == "beads" {
				t = strings.Join(parts[3:], "/")
				internal = true
			} else {
				return "", "", fragment, false, host, "external"
			}
		case "beads.gascity.com":
			t = strings.TrimPrefix(u.Path, "/")
			if !strings.HasPrefix(t, "docs/") {
				t = "docs/" + t
			}
			internal = true
		default:
			return "", "", fragment, false, host, "external"
		}
	} else {
		internal = true
	}

	if i := strings.IndexByte(t, '#'); i >= 0 {
		fragment = t[i:]
		t = t[:i]
	}
	if i := strings.IndexByte(t, '?'); i >= 0 {
		t = t[:i]
	}
	if t == "" {
		return cleanDocPath(sourceRel), memoryID(sourceRel), fragment, true, host, "local-fragment"
	}

	// Mintlify redirects are routing metadata, not citations. They are used
	// only to resolve an authored link to its canonical target node.
	if redirects != nil {
		route := t
		if !strings.HasPrefix(route, "/") {
			route = "/" + strings.TrimPrefix(route, "docs/")
		}
		if dest, ok := redirects[route]; ok {
			t = "docs/" + strings.TrimPrefix(dest, "/")
		}
	}

	var base string
	if strings.HasPrefix(t, "/") {
		base = strings.TrimPrefix(t, "/")
		// Mintlify site links are rooted at docs/, not repository root.
		if _, ok := lookupKnown(base, known); !ok && !strings.HasPrefix(base, "docs/") {
			base = "docs/" + base
		}
	} else if strings.HasPrefix(t, "docs/") || strings.HasPrefix(t, "engdocs/") || (!strings.HasPrefix(t, ".") && known[cleanDocPath(t)] != "") {
		base = t
	} else {
		base = filepath.ToSlash(filepath.Clean(filepath.Join(filepath.Dir(sourceRel), t)))
	}

	if p, ok := lookupKnown(base, known); ok {
		return p, known[cleanDocPath(p)], fragment, true, host, "internal-resolved"
	}
	return cleanDocPath(base), "", fragment, true, host, "internal-unresolved"
}

func fragmentValue(s string) string {
	if s == "" {
		return ""
	}
	return "#" + s
}

func sourceURL(ref, rel string) string {
	if strings.TrimSpace(ref) == "" {
		ref = "main"
	}
	return sourceRepo + "/blob/" + ref + "/" + filepath.ToSlash(rel)
}

func lookupKnown(p string, known map[string]string) (string, bool) {
	p = strings.TrimPrefix(filepath.ToSlash(filepath.Clean(p)), "./")
	candidates := []string{p, cleanDocPath(p)}
	if !strings.HasSuffix(strings.ToLower(p), ".md") && !strings.HasSuffix(strings.ToLower(p), ".mdx") {
		candidates = append(candidates, p+".md", p+".mdx", p+"/index.md", p+"/index.mdx")
	}
	for _, c := range candidates {
		if _, ok := known[cleanDocPath(c)]; ok {
			return c, true
		}
	}
	return "", false
}

func WriteJSON(path string, v []model.Memory) error {
	return fmt.Errorf("WriteJSON not implemented; use cmd/memtrial -emit-corpus")
}
