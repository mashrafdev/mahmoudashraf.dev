import { transformerNotationWordHighlight } from '@shikijs/transformers';
import { codeToHtml } from 'shiki';

async function highlightCodeBlock(code, lang, theme) {
  return codeToHtml(code, {
    lang,
    theme,
    transformers: [
      transformerNotationWordHighlight({
        matchAlgorithm: 'v3',
      }),
    ],
  });
}

const [, , rawCode, lang, theme] = process.argv;
highlightCodeBlock(rawCode, lang, theme).then(console.log).catch(console.error);
