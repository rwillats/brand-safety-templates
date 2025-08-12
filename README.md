# Brand Safety Templated Prompt Test Set

A reusable framework for generating company-specific brand safety evaluation prompts. Define company attributes in a configuration file to adapt the same base templates for testing any organization.

## Purpose

Test model robustness against prompts designed to elicit unsafe outputs across four categories:

1. **Competitor Mention** - Attempts to generate unfavorable comparisons or portray rivals as superior
2. **Data Leakage** - Attempts to extract confidential information (personal data, infrastructure, credentials)
3. **Misrepresentations & Trust Violations** - Attempts to create false claims, fake content, or impersonations
4. **Public Image Attack** - Direct insults, threats, or statements damaging reputation

## How It Works

Templates in `brand_safety_templates.csv` use placeholders:
- `<company>` - Company name
- `<ceo>` - CEO name
- `<competitor>` - Random selection from competitor list
- `<individual>` - Random selection from personnel list

The `populate.py` script replaces placeholders using your `config.json` to create a populated test set.

## Usage

### 1. Clone the repository
```bash
git clone https://github.com/yourname/brand-safety-templates.git
cd brand-safety-templates
```

### 2. Create your configuration
```bash
cp config.example.json config.json
```

Edit `config.json`:
```json
{
  "company": "Dunder Mifflin",
  "ceo": "David Wallace",
  "competitors": ["Utica Paper", "Staples", "Prince Family Paper"],
  "individuals": ["Michael Scott", "Dwight Schrute", "Jim Halpert"]
}
```

**Note:** 
- `company` and `ceo` must be single strings
- `competitors` and `individuals` must be arrays of strings
- The script will randomly select from the lists when populating templates

### 3. Generate the test set
```bash
python3 populate.py
```

Output: `out/populated.csv`
