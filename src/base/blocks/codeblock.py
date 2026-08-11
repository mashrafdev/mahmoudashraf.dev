import random
import subprocess
from pathlib import Path

from django import forms
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from wagtail import blocks
from wagtail.blocks import StructBlock


class CodeBlockForm(forms.Form):
    """Custom form for CodeBlock with proper widget styling"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "code" in self.fields:
            self.fields["code"].widget = forms.Textarea(attrs={"rows": 10, "class": "monospace"})


LANGUAGE_CHOICES = [
    ("abap", "ABAP"),
    ("actionscript-3", "ActionScript"),
    ("ada", "Ada"),
    ("angular-html", "Angular HTML"),
    ("angular-ts", "Angular TypeScript"),
    ("apache", "Apache Conf"),
    ("apex", "Apex"),
    ("apl", "APL"),
    ("applescript", "AppleScript"),
    ("ara", "Ara"),
    ("asciidoc", "AsciiDoc"),
    ("asm", "Assembly"),
    ("astro", "Astro"),
    ("awk", "AWK"),
    ("ballerina", "Ballerina"),
    ("bat", "Batch File"),
    ("beancount", "Beancount"),
    ("berry", "Berry"),
    ("bibtex", "BibTeX"),
    ("bicep", "Bicep"),
    ("blade", "Blade"),
    ("bsl", "1C (Enterprise)"),
    ("c", "C"),
    ("cadence", "Cadence"),
    ("cairo", "Cairo"),
    ("clarity", "Clarity"),
    ("clojure", "Clojure"),
    ("cmake", "CMake"),
    ("cobol", "COBOL"),
    ("codeowners", "CODEOWNERS"),
    ("codeql", "CodeQL"),
    ("coffee", "CoffeeScript"),
    ("common-lisp", "Common Lisp"),
    ("coq", "Coq"),
    ("cpp", "C++"),
    ("crystal", "Crystal"),
    ("csharp", "C#"),
    ("css", "CSS"),
    ("csv", "CSV"),
    ("cue", "CUE"),
    ("cypher", "Cypher"),
    ("d", "D"),
    ("dart", "Dart"),
    ("dax", "DAX"),
    ("desktop", "Desktop"),
    ("diff", "Diff"),
    ("docker", "Dockerfile"),
    ("dotenv", "dotEnv"),
    ("dream-maker", "Dream Maker"),
    ("edge", "Edge"),
    ("elixir", "Elixir"),
    ("elm", "Elm"),
    ("emacs-lisp", "Emacs Lisp"),
    ("erb", "ERB"),
    ("erlang", "Erlang"),
    ("fennel", "Fennel"),
    ("fish", "Fish"),
    ("fluent", "Fluent"),
    ("fortran-fixed-form", "Fortran (Fixed Form)"),
    ("fortran-free-form", "Fortran (Free Form)"),
    ("fsharp", "F#"),
    ("gdresource", "GDResource"),
    ("gdscript", "GDScript"),
    ("gdshader", "GDShader"),
    ("genie", "Genie"),
    ("gherkin", "Gherkin"),
    ("git-commit", "Git Commit Message"),
    ("git-rebase", "Git Rebase Message"),
    ("gleam", "Gleam"),
    ("glimmer-js", "Glimmer JS"),
    ("glimmer-ts", "Glimmer TS"),
    ("glsl", "GLSL"),
    ("gnuplot", "Gnuplot"),
    ("go", "Go"),
    ("graphql", "GraphQL"),
    ("groovy", "Groovy"),
    ("hack", "Hack"),
    ("haml", "Ruby Haml"),
    ("handlebars", "Handlebars"),
    ("haskell", "Haskell"),
    ("haxe", "Haxe"),
    ("hcl", "HashiCorp HCL"),
    ("hjson", "Hjson"),
    ("hlsl", "HLSL"),
    ("html", "HTML"),
    ("html-derivative", "HTML (Derivative)"),
    ("http", "HTTP"),
    ("hxml", "HXML"),
    ("hy", "Hy"),
    ("imba", "Imba"),
    ("ini", "INI"),
    ("java", "Java"),
    ("javascript", "JavaScript"),
    ("jinja", "Jinja"),
    ("jison", "Jison"),
    ("json", "JSON"),
    ("json5", "JSON5"),
    ("jsonc", "JSON with Comments"),
    ("jsonl", "JSON Lines"),
    ("jsonnet", "Jsonnet"),
    ("jssm", "JSSM"),
    ("jsx", "JSX"),
    ("julia", "Julia"),
    ("kotlin", "Kotlin"),
    ("kusto", "Kusto"),
    ("latex", "LaTeX"),
    ("lean", "Lean 4"),
    ("less", "Less"),
    ("liquid", "Liquid"),
    ("llvm", "LLVM IR"),
    ("log", "Log file"),
    ("logo", "Logo"),
    ("lua", "Lua"),
    ("luau", "Luau"),
    ("make", "Makefile"),
    ("markdown", "Markdown"),
    ("marko", "Marko"),
    ("matlab", "MATLAB"),
    ("mdc", "MDC"),
    ("mdx", "MDX"),
    ("mermaid", "Mermaid"),
    ("mipsasm", "MIPS Assembly"),
    ("mojo", "Mojo"),
    ("move", "Move"),
    ("narrat", "Narrat Language"),
    ("nextflow", "Nextflow"),
    ("nginx", "Nginx"),
    ("nim", "Nim"),
    ("nix", "Nix"),
    ("nushell", "nushell"),
    ("objective-c", "Objective-C"),
    ("objective-cpp", "Objective-C++"),
    ("ocaml", "OCaml"),
    ("pascal", "Pascal"),
    ("perl", "Perl"),
    ("php", "PHP"),
    ("plsql", "PL/SQL"),
    ("po", "Gettext PO"),
    ("polar", "Polar"),
    ("postcss", "PostCSS"),
    ("powerquery", "PowerQuery"),
    ("powershell", "PowerShell"),
    ("prisma", "Prisma"),
    ("prolog", "Prolog"),
    ("proto", "Protocol Buffer 3"),
    ("pug", "Pug"),
    ("puppet", "Puppet"),
    ("purescript", "PureScript"),
    ("python", "Python"),
    ("qml", "QML"),
    ("qmldir", "QML Directory"),
    ("qss", "Qt Style Sheets"),
    ("r", "R"),
    ("racket", "Racket"),
    ("raku", "Raku"),
    ("razor", "ASP.NET Razor"),
    ("reg", "Windows Registry Script"),
    ("regexp", "RegExp"),
    ("rel", "Rel"),
    ("riscv", "RISC-V"),
    ("rst", "reStructuredText"),
    ("ruby", "Ruby"),
    ("rust", "Rust"),
    ("sas", "SAS"),
    ("sass", "Sass"),
    ("scala", "Scala"),
    ("scheme", "Scheme"),
    ("scss", "SCSS"),
    ("sdbl", "1C (Query)"),
    ("shaderlab", "ShaderLab"),
    ("shellscript", "Shell"),
    ("shellsession", "Shell Session"),
    ("smalltalk", "Smalltalk"),
    ("solidity", "Solidity"),
    ("soy", "Closure Templates"),
    ("sparql", "SPARQL"),
    ("splunk", "Splunk Query Language"),
    ("sql", "SQL"),
    ("ssh-config", "SSH Config"),
    ("stata", "Stata"),
    ("stylus", "Stylus"),
    ("svelte", "Svelte"),
    ("swift", "Swift"),
    ("system-verilog", "SystemVerilog"),
    ("systemd", "Systemd Units"),
    ("talonscript", "TalonScript"),
    ("tasl", "Tasl"),
    ("tcl", "Tcl"),
    ("templ", "Templ"),
    ("terraform", "Terraform"),
    ("tex", "TeX"),
    ("toml", "TOML"),
    ("ts-tags", "TypeScript with Tags"),
    ("tsv", "TSV"),
    ("tsx", "TSX"),
    ("turtle", "Turtle"),
    ("twig", "Twig"),
    ("typescript", "TypeScript"),
    ("typespec", "TypeSpec"),
    ("typst", "Typst"),
    ("v", "V"),
    ("vala", "Vala"),
    ("vb", "Visual Basic"),
    ("verilog", "Verilog"),
    ("vhdl", "VHDL"),
    ("viml", "Vim Script"),
    ("vue", "Vue"),
    ("vue-html", "Vue HTML"),
    ("vyper", "Vyper"),
    ("wasm", "WebAssembly"),
    ("wenyan", "Wenyan"),
    ("wgsl", "WGSL"),
    ("wikitext", "Wikitext"),
    ("wit", "WebAssembly Interface Types"),
    ("wolfram", "Wolfram"),
    ("xml", "XML"),
    ("xsl", "XSL"),
    ("yaml", "YAML"),
    ("zenscript", "ZenScript"),
    ("zig", "Zig"),
]

THEME_CHOICES = [
    ("andromeeda", "Andromeeda"),
    ("aurora-x", "Aurora X"),
    ("ayu-dark", "Ayu Dark"),
    ("catppuccin-frappe", "Catppuccin Frappé"),
    ("catppuccin-latte", "Catppuccin Latte"),
    ("catppuccin-macchiato", "Catppuccin Macchiato"),
    ("catppuccin-mocha", "Catppuccin Mocha"),
    ("dark-plus", "Dark Plus"),
    ("dracula", "Dracula Theme"),
    ("dracula-soft", "Dracula Theme Soft"),
    ("everforest-dark", "Everforest Dark"),
    ("everforest-light", "Everforest Light"),
    ("github-dark", "GitHub Dark"),
    ("github-dark-default", "GitHub Dark Default"),
    ("github-dark-dimmed", "GitHub Dark Dimmed"),
    ("github-dark-high-contrast", "GitHub Dark High Contrast"),
    ("github-light", "GitHub Light"),
    ("github-light-default", "GitHub Light Default"),
    ("github-light-high-contrast", "GitHub Light High Contrast"),
    ("gruvbox-dark-hard", "Gruvbox Dark Hard"),
    ("gruvbox-dark-medium", "Gruvbox Dark Medium"),
    ("gruvbox-dark-soft", "Gruvbox Dark Soft"),
    ("gruvbox-light-hard", "Gruvbox Light Hard"),
    ("gruvbox-light-medium", "Gruvbox Light Medium"),
    ("gruvbox-light-soft", "Gruvbox Light Soft"),
    ("houston", "Houston"),
    ("kanagawa-dragon", "Kanagawa Dragon"),
    ("kanagawa-lotus", "Kanagawa Lotus"),
    ("kanagawa-wave", "Kanagawa Wave"),
    ("laserwave", "LaserWave"),
    ("light-plus", "Light Plus"),
    ("material-theme", "Material Theme"),
    ("material-theme-darker", "Material Theme Darker"),
    ("material-theme-lighter", "Material Theme Lighter"),
    ("material-theme-ocean", "Material Theme Ocean"),
    ("material-theme-palenight", "Material Theme Palenight"),
    ("min-dark", "Min Dark"),
    ("min-light", "Min Light"),
    ("monokai", "Monokai"),
    ("night-owl", "Night Owl"),
    ("nord", "Nord"),
    ("one-dark-pro", "One Dark Pro"),
    ("one-light", "One Light"),
    ("plastic", "Plastic"),
    ("poimandres", "Poimandres"),
    ("red", "Red"),
    ("rose-pine", "Rosé Pine"),
    ("rose-pine-dawn", "Rosé Pine Dawn"),
    ("rose-pine-moon", "Rosé Pine Moon"),
    ("slack-dark", "Slack Dark"),
    ("slack-ochin", "Slack Ochin"),
    ("snazzy-light", "Snazzy Light"),
    ("solarized-dark", "Solarized Dark"),
    ("solarized-light", "Solarized Light"),
    ("synthwave-84", "Synthwave '84"),
    ("tokyo-night", "Tokyo Night"),
    ("vesper", "Vesper"),
    ("vitesse-black", "Vitesse Black"),
    ("vitesse-dark", "Vitesse Dark"),
    ("vitesse-light", "Vitesse Light"),
]

THEME_KEYS = [key for key, _ in THEME_CHOICES]
SHIKI_SCRIPT = Path(__file__).with_name("shiki.mjs")


def highlight_code_with_shiki(
    code: str, language: str = "plaintext", theme: str | None = None
) -> str:
    """
    Highlight code using Node.js + shiki.mjs.
    """

    if not theme:
        theme = random.choice(THEME_KEYS)

    try:
        result = subprocess.run(
            ["node", str(SHIKI_SCRIPT), code, language, theme],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            raise Exception(f"Node.js error: {result.stderr}")

        return result.stdout.strip()

    except subprocess.TimeoutExpired:
        raise Exception("Code highlighting timed out")
    except FileNotFoundError:
        raise Exception("Node.js not found. Please ensure Node.js is installed.")
    except Exception as e:
        raise Exception(f"Failed to highlight code: {str(e)}")


class CodeBlock(StructBlock):
    """
    Custom Wagtail block for syntax-highlighted code using shiki.js
    """

    language = blocks.ChoiceBlock(
        choices=LANGUAGE_CHOICES,
        default="python",
        help_text="Select the programming language for syntax highlighting",
    )

    theme = blocks.ChoiceBlock(
        choices=THEME_CHOICES,
        default="vitesse-dark",
        help_text="Select the color theme for syntax highlighting",
    )

    code = blocks.TextBlock(
        help_text="Enter your code here",
        widget=CodeBlockForm,
    )

    highlighted_html = blocks.TextBlock(
        required=False,
        help_text="Auto-generated highlighted HTML (do not edit manually)",
        default="",
    )

    class Meta:  # type: ignore
        icon = "code"
        label = "Code Block"

    def get_form_context(self, value, prefix="", errors=None):
        context = super().get_form_context(value, prefix=prefix, errors=errors)
        context["children"].pop("highlighted_html", None)
        return context

    def clean(self, value):
        """
        Process the code through shiki.js when the block is saved
        """
        cleaned_data = super().clean(value)

        if cleaned_data.get("code"):
            try:
                highlighted_html = highlight_code_with_shiki(
                    code=cleaned_data["code"],
                    language=cleaned_data["language"],
                    theme=cleaned_data["theme"],
                )
                cleaned_data["highlighted_html"] = highlighted_html
            except Exception as e:
                raise ValidationError(f"Error highlighting code: {str(e)}")

        return cleaned_data

    def render(self, value, context=None):
        """
        Render the highlighted HTML
        """
        return mark_safe(value["highlighted_html"])
