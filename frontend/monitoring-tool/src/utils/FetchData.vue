<template>
    <div>
      <div v-for="(item, index) in accordionItems" :key="index" class="accordion">
        <div @click="toggleAccordion(index)" class="accordion-header">
          <div>{{ item.site }}</div>
          <div :style="{ color: item.status === 'up' ? 'green' : 'red' }">Status: {{ item.status }}</div>
        </div>
        <div v-if="item.isOpen" class="accordion-content">
          <div>Response Time: {{ item.responsetime }} ms<br></div>
          <div>Time: {{ item.time }}</div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        accordionItems: [],
      };
    },
    mounted() {
      this.fetchData();
      setInterval(this.fetchData, 60000); // Fetch every minute (60000 milliseconds)
    },
    methods: {
      async fetchData() {
        try {
          const response = await fetch('http://localhost:8000/fetch_newest');
          if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
          }
  
          const data = await response.json();
          this.accordionItems = data.all_data.map(item => ({ ...item, isOpen: false }));
          console.log(data);
        } catch (error) {
          console.error('Error fetching data:', error);
        }
      },
      toggleAccordion(index) {
        // Toggle the isOpen state for the clicked accordion item
        this.accordionItems[index].isOpen = !this.accordionItems[index].isOpen;
      },
    }
  };
  </script>
  
<style scoped>
  .accordion {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }

  .accordion-header {
    cursor: pointer;
    padding: 10px;
    background-color: #fafafa;
    border: 1px solid #ddd;
    border-bottom: none;
    width: 600px;
    display: flex;
    justify-content: space-between;
  }

  .accordion-content {
    padding: 10px;
    border: 1px solid #ddd;
    width: 600px;
    display: flex;
    flex-direction: row;
    justify-content: space-between;
  }
</style>