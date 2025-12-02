import adapter from '@sveltejs/adapter-auto'
import preprocess from 'svelte-preprocess'
import { plugin as md, Mode } from 'vite-plugin-markdown'

/** @type {import('@sveltejs/kit').Config} */
const config = {
	preprocess: preprocess(),

	kit: {
		adapter: adapter(),
		target: '#svelte',
		vite: {
			plugins: [
				md({
					mode: Mode.HTML,
					markdownIt: { typography: true },
				}),
			],
		},
	},
}

export default config