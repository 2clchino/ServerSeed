import { createRouter, createWebHistory } from 'vue-router';
import Page01 from './components/Page01.vue';
import Page02 from './components/Page02.vue';
import NotFound from './components/NotFound.vue';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/page01' },
    { name: 'test1', path: '/page01', component: Page01 },
    { name: 'test2', path: '/page02', component: Page02 },
    { path: '/:notFound(.*)', component: NotFound }
  ],
  linkActiveClass: 'example-active',
  linkExactActiveClass: 'example-exact-active',
});

export default router;