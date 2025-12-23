import aerial from "../lib/assets/aerial.png"
import dji from "../lib/assets/dji.png"
import drl from "../lib/assets/drl.png"
import flying_drone from "../lib/assets/flying_drone.png"
import spray from "../lib/assets/spray.png"
import stor from "../lib/assets/stor.png"

export const filterOptions = [
    {
        label: 'Featured', 
        value: 'featured'
    },
    {
        label: 'Price: Low -> High',
        value: 'price-asc'
    },
    {
        label: 'Price: High -> Low',
        value: 'price-desc'
    },
    {
        label: 'Top Rated',
        value: 'rating'
    }
]

export const filterCategoryOptions = [
    {
        label: 'All',
        value: 'All'
    },
    {
        label: 'Multirotor',
        value: 'Multirotor'
    },
    {
        label: 'Fixed-wing',
        value: 'Fixed-wing'
    }
]

export const listBrands = [dji, aerial, drl, flying_drone, spray, stor]

export const roleList = [
     {
        label: 'Admin', 
        value: 'ADMIN'
    },
    {
        label: 'Employee',
        value: 'EMPLOYEE'
    },
]
