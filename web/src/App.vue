<template>
  <div>
    <a href="#" @click="setPage('page01')">Page01</a>
    <a href="#" @click="setPage('page02')">Page02</a>
    <a href="#" @click="callAPI()">Call API</a>
  </div>
  <component :is="activePage"></component>
</template>

<script>
import axios from "axios";
import Page01 from './components/Page01.vue'
import Page02 from './components/Page02.vue'

export default {
  name: 'App',
  components: {
    Page01, Page02
  },
  data() {
    return {
      activePage: 'page01'
    }
  },
  methods: {
    setPage(page) {
       this.activePage = page;
    },
    callAPI() {
      axios.get("http://localhost:5000").then(response => {
        console.log(response.data.message);
      });
    }
  }
}
</script>