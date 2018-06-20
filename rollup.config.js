import svelte from 'rollup-plugin-svelte';
import resolve from 'rollup-plugin-node-resolve';
import commonjs from 'rollup-plugin-commonjs';
import buble from 'rollup-plugin-buble';
import uglify from 'rollup-plugin-uglify';
import html from 'rollup-plugin-fill-html';
import cleaner from 'rollup-plugin-cleaner';
import url from 'rollup-plugin-url';

const production = !process.env.ROLLUP_WATCH;

export default {
	input: 'app/main.js',
	output: {
		sourcemap: true,
		format: 'iife',
		name: 'app',
		file: 'public/bundle.[hash].js'
	},
	plugins: [
        // remove destination dir before every build
        cleaner({
            targets: ['./public/'],
        }),

		svelte({
			// opt in to v3 behaviour today
			skipIntroByDefault: true,
			nestedTransitions: true,

			// enable runtime checks in dev mode
			dev: !production,

			// extract css into separate file
			css: css => {
				css.write('public/bundle.[hash].css');
			}
		}),

		resolve(),
		commonjs(),
		url(),

		production && buble({ include: ['src/**', 'node_modules/svelte/shared.js'] }),
		production && uglify(),

		// Add js and css to `app/index.html` and copy to `public` dir
        html({
            template: 'app/index.html',
            filename: 'index.html',
        })
	]
};